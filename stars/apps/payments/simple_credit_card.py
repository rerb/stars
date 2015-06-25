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
    """
        Processes credit card payments.
    """
    def process_subscription_payment(self,
                                     subscription,
                                     user,
                                     amount,
                                     card_num,
                                     exp_date,
                                     cvv):
        """
            Processes a subscription credit card payment.
        """
        product = {'price': amount,
                   'quantity': 1,
                   'name': 'STARS Subscription Purchase'}

        result = self._process_payment(card_num=card_num,
                                       exp_date=exp_date,
                                       cvv=cvv,
                                       products=[product])

        if result['cleared'] and result['trans_id']:

            payment = stars.apps.institutions.models.SubscriptionPayment(
                subscription=subscription,
                date=datetime.now(),
                amount=amount,
                user=user,
                method='credit',
                confirmation=str(result['trans_id']))
            payment.save()

        else:
            raise CreditCardProcessingError(result['msg'])

        return payment

    def _process_payment(self,
                         card_num,
                         exp_date,
                         cvv,
                         products,
                         login=settings.AUTHORIZENET_LOGIN,
                         key=settings.AUTHORIZENET_KEY):
        """
            Connects to Authorize.net and processes a payment.

            products: [{'name': '', 'price': #.#, 'quantity': #},]
        """
        client = AuthorizeClient(login,
                                 key,
                                 test=False,
                                 debug=settings.AUTHORIZE_CLIENT_DEBUG)
        # exp_date is MMYYYY.
        year = int(exp_date[2:])
        month = int(exp_date[:2])

        try:
            cc = CreditCard(card_num, year, month, cvv)
        except Exception as ex:
            raise CreditCardProcessingError(str(ex))

        total = 0.0
        for product in products:
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
