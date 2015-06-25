import ast
from datetime import datetime
from logging import getLogger

from authorize import AuthorizeClient, AuthorizeResponseError, CreditCard
from django.conf import settings

import stars.apps.institutions.models

logger = getLogger('stars')


class CreditCardProcessingError(Exception):
    pass


class CreditCardPaymentProcessor(object):

    def process_subscription_payment(self,
                                     subscription,
                                     amount,
                                     user,
                                     form):
        """
            Processes a subscription credit card payment.
        """
        result = self.process_payment_form(
            amount=amount,
            user=user,
            form=form,
            product_name='STARS Test Subscription')

        if result['cleared'] and result['trans_id']:

            payment = stars.apps.institutions.models.SubscriptionPayment(
                subscription=subscription,
                date=datetime.now(),
                amount=amount,
                user=user,
                method='credit',
                confirmation=str(result['trans_id']))
            payment.save()

            subscription.amount_due -= amount
            if not subscription.amount_due:
                subscription.paid_in_full = True
            subscription.save()

        else:
            raise CreditCardProcessingError(result['msg'])

        return payment, self._get_payment_context(pay_form=form)

    def process_payment_form(self,
                             amount,
                             user,
                             form,
                             product_name="STARS Subscription Purchase"):
        """
            A simple payment processing form for the reg process
        """
        payment_context = self._get_payment_context(pay_form=form)

        product_dict = {'price': amount,
                        'quantity': 1,
                        'name':  product_name}

        result = self._process_payment(payment_context=payment_context,
                                       product_list=[product_dict])

        return result

    def _get_payment_context(self, pay_form):
        """
            Extracts the payment context for process_payment from a
            given form.
        """
        payment_context = {
            'cc_number': pay_form.cleaned_data['card_number'],
            'exp_date': (pay_form.cleaned_data['exp_month'] +
                         pay_form.cleaned_data['exp_year']),
            'cv_number': pay_form.cleaned_data['cv_code']
        }

        return payment_context

    def _process_payment(self, payment_context, product_list,
                         login=settings.AUTHORIZENET_LOGIN,
                         key=settings.AUTHORIZENET_KEY):
        """
            Connects to Authorize.net and processes a payment.

            payment_context: {'exp_date': '', 'cc_number': '',
                              'cv_number': ''}

            product_list: [{'name': '', 'price': #.#, 'quantity': #},]
        """
        client = AuthorizeClient(login,
                                 key,
                                 test=False,
                                 debug=settings.AUTHORIZE_CLIENT_DEBUG)

        # exp_date is MMYYYY.
        year = int(payment_context['exp_date'][2:])
        month = int(payment_context['exp_date'][:2])

        try:
            cc = CreditCard(payment_context['cc_number'],
                            year,
                            month,
                            payment_context['cv_number'])
        except Exception as ex:
            raise CreditCardProcessingError(str(ex))

        total = 0.0
        for product in product_list:
            total += product['price'] * product['quantity']

        try:
            transaction = client.card(cc).capture(total)
        except AuthorizeResponseError as exc:
            logger.error("Payment denied. %s" % str(exc))
            return {'cleared': False,
                    'reason_code': exc.full_response['response_reason_code'],
                    'msg': exc.full_response['response_reason_text'],
                    'conf': None,
                    'trans_id': None}

        if transaction.full_response['response_code'] == '1':
            # Success.
            return {'cleared': True,
                    'reason_code': None,
                    'msg': None,
                    'conf': transaction.full_response['authorization_code'],
                    'trans_id': transaction.full_response['transaction_id']}
        else:
            logger.error("Payment denied. %s" % transaction.full_response[
                'response_reason_text'])
            return {'cleared': False,
                    'reason_code': transaction.full_response[
                        'response_reason_code'],
                    'msg': transaction.full_response['response_reason_text'],
                    'conf': transaction.full_response['authorization_code'],
                    'trans_id': transaction.full_response['transaction_id']}
