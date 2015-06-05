from datetime import datetime
from logging import getLogger

from authorize import AuthorizeClient, CreditCard
from django.conf import settings
from django.forms.models import model_to_dict

import stars.apps.institutions.models
from utils import is_canadian_zipcode

logger = getLogger('stars')


class CreditCardProcessingError(Exception):
    pass


class CreditCardPaymentProcessor(object):
    """
        Processes credit card payments.
    """

    def process_payment_form(self,
                             contact_info,
                             amount,
                             user,
                             form,
                             invoice_num,
                             product_name=None):
        """
            A simple payment processing form for the reg process
        """
        payment_context = self._get_payment_context(
            pay_form=form,
            contact_info=contact_info)

        if not product_name:
            product_name = "STARS Subscription Purchase"

        product_dict = {'price': amount,
                        'quantity': 1,
                        'name':  product_name}

        result = self._process_payment(
            payment_context=payment_context,
            product_list=[product_dict],
            invoice_num=invoice_num)

        return result

    def process_subscription_payment(self, subscription, amount, user, form):
        """
            Processes a subscription credit card payment.
        """

        result = self.process_payment_form(
            model_to_dict(subscription.institution),
            amount,
            user,
            form,
            invoice_num=subscription.institution.aashe_id)

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

        return payment, self._get_payment_context(
            pay_form=form,
            contact_info=model_to_dict(subscription.institution))

    def _get_payment_context(self, pay_form, contact_info):
        """
            Extracts the payment context for process_payment from a
            given form and institution.

            @todo - make this more generic, so it doesn't rely on institution
        """
        cc = pay_form.cleaned_data['card_number']
        l = len(cc)
        if l >= 4:
            last_four = cc[l-4:l]
        else:
            last_four = None

        payment_context = {
            'name_on_card': pay_form.cleaned_data['name_on_card'],
            'cc_number': pay_form.cleaned_data['card_number'],
            'exp_date': (pay_form.cleaned_data['exp_month'] +
                         pay_form.cleaned_data['exp_year']),
            'cv_number': pay_form.cleaned_data['cv_code'],
            'billing_address': pay_form.cleaned_data['billing_address'],
            'billing_address_line_2': (
                pay_form.cleaned_data['billing_address_line_2']),
            'billing_city': pay_form.cleaned_data['billing_city'],
            'billing_state': pay_form.cleaned_data['billing_state'],
            'billing_zipcode': pay_form.cleaned_data['billing_zipcode'],
            'country': "USA",

            # contact info from the institution
            'billing_firstname': contact_info['contact_first_name'],
            'billing_lastname': contact_info['contact_last_name'],
            'billing_email': contact_info['contact_email'],
            'description': "{inst} STARS Registration ({when})".format(
                inst=contact_info['contact_last_name'],
                when=datetime.now().isoformat()),
            # 'company': contact_info['name'],
            'last_four': last_four,
        }

        if is_canadian_zipcode(pay_form.cleaned_data['billing_zipcode']):
            payment_context['country'] = "Canada"

        return payment_context

    def _process_payment(self, payment_context, product_list,
                         invoice_num=None, login=None, key=None):
        """
            Connects to Authorize.net and processes a payment based on the
            payment information in payment_dict and the product_dict

            payment_dict: {first_name, last_name, street, city, state,
            zip, country, email, cc_number, expiration_date}

            product_list: [{'name': '', 'price': #.#, 'quantity': #},]

            login and key: optional parameters for Auth.net
            connections (for testing)

            returns:
                {'cleared': cleared,
                'reason_code': reason_code,
                'msg': msg,
                'conf': "" }
        """
        login = login or settings.AUTHORIZENET_LOGIN
        assert login is not None, "login is required"

        key = key or settings.AUTHORIZENET_KEY
        assert key is not None, "key is required"

        client = AuthorizeClient(settings.AUTHORIZENET_LOGIN,
                                 settings.AUTHORIZENET_KEY,
                                 debug=settings.DEBUG)

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

        transaction = client.card(cc).capture(total)

        if transaction.full_response['response_code'] == '1':
            # Success.
            return {'cleared': True,
                    'reason_code': None,
                    'msg': None,
                    'conf': transaction.full_response['authorization_code'],
                    'trans_id': transaction.full_response['transaction_id']}
        else:
            msg = ("Payment denied for %s %s (%s)" %
                   (payment_context['billing_firstname'],
                    payment_context['billing_lastname'],
                    transaction.full_response['response_reason_text']))
            logger.error(msg)
            return {'cleared': False,
                    'reason_code': transaction.full_response['response_code'],
                    'msg': transaction.full_response['response_reason_text'],
                    'conf': None,
                    'trans_id': None}
