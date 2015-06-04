from datetime import datetime
from logging import getLogger

from authorize import AuthorizeClient, CreditCard
from django.conf import settings

import stars.apps.institutions.models

logger = getLogger('stars')


class CreditCardProcessingError(Exception):
    pass


class CreditCardPaymentProcessor(object):
    """
        Processes credit card payments.
    """
    def process_payment_form(self,
                             amount,
                             card_num,
                             exp_date,
                             cvv,
                             invoice_num):
        """
            A simple payment processing form for the reg process
        """
        product_name = "STARS Subscription Purchase"

        product_dict = {'price': amount,
                        'quantity': 1,
                        'name':  product_name}

        result = self._process_payment(
            card_num=card_num,
            exp_date=exp_date,
            cvv=cvv,
            products=[product_dict],
            invoice_num=invoice_num)

        return result

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
        result = self.process_payment_form(
            amount=amount,
            card_num=card_num,
            exp_date=exp_date,
            cvv=cvv,
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

        else:
            raise CreditCardProcessingError(result['msg'])

        return payment

    def _process_payment(self,
                         card_num,
                         exp_date,
                         cvv,
                         invoice_num,
                         products):

        """
            Connects to Authorize.net and processes a payment.

            products: [{'name': '', 'price': #.#, 'quantity': #},]

            server, login, and key: optional parameters for Auth.net
            connections (for testing)

            returns:
                {'cleared': cleared,
                 'reason_code': reason_code,
                 'msg': msg,
                 'conf': confirmation_code,
                 'trans_id': transaction_id}
        """
        # Assertions below help when debugging tests that fail because
        # settings.AUTHORIZENET_* aren't set.
        assert ((settings.AUTHORIZENET_SERVER is not None and
                 settings.AUTHORIZENET_LOGIN is not None and
                 settings.AUTHORIZENET_KEY is not None),
                'settings.AUTHORIZE_SERVER, settings.AUTHORIZE_LOGIN and '
                'settings.AUTHORIZE_KEY are required.')

        client = AuthorizeClient(settings.AUTHORIZENET_LOGIN,
                                 settings.AUTHORIZENET_KEY,
                                 debug=True)
        # authorize sauce doesn't need server passed in?
        # is it hard-coded to the production authorize.net?

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

        transaction = client.card(cc).capture(total)

        if transaction.full_response['response_code'] == '1':
            # Success.
            return {'cleared': True,
                    'reason_code': None,
                    'msg': None,
                    'conf': transaction.full_response['authorization_code'],
                    'trans_id': transaction.full_response['transaction_id']}
        else:
            logger.error("Payment denied. %s" %
                         transaction.full_response['response_reason_text'])
            return {'cleared': False,
                    'reason_code': transaction.full_response['response_code'],
                    'msg': transaction.full_response['response_reason_text'],
                    'conf': None,
                    'trans_id': None}
