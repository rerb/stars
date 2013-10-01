from datetime import datetime
from logging import getLogger

from django.conf import settings
from django.forms.models import model_to_dict

from zc.authorizedotnet.processing import CcProcessor

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
                             amount,
                             card_num,
                             exp_date,
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
            products=[product_dict],
            invoice_num=invoice_num)

        return result

    def process_subscription_payment(self,
                                     subscription,
                                     user,
                                     amount,
                                     card_num,
                                     exp_date):
        """
            Processes a subscription credit card payment.
        """
        result = self.process_payment_form(
            amount=amount,
            card_num=card_num,
            exp_date=exp_date,
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

#     def _get_payment_context(self, pay_form, contact_info):
#         """
#             Extracts the payment context for process_payment from a
#             given form and institution.

#             @todo - make this more generic, so it doesn't rely on institution
#         """
#         cc = pay_form.cleaned_data['card_number']
#         l = len(cc)
#         if l >= 4:
#             last_four = cc[l-4:l]
#         else:
#             last_four = None

#         payment_context = {
#             'name_on_card': pay_form.cleaned_data['name_on_card'],
#             'cc_number': pay_form.cleaned_data['card_number'],
#             'exp_date': (pay_form.cleaned_data['exp_month'] +
#                          pay_form.cleaned_data['exp_year']),
#             'cv_number': pay_form.cleaned_data['cv_code'],
#             'billing_address': pay_form.cleaned_data['billing_address'],
#             'billing_address_line_2': (
#                 pay_form.cleaned_data['billing_address_line_2']),
#             'billing_city': pay_form.cleaned_data['billing_city'],
#             'billing_state': pay_form.cleaned_data['billing_state'],
#             'billing_zipcode': pay_form.cleaned_data['billing_zipcode'],
#             'country': "USA",

#             # contact info from the institution
#             'billing_firstname': contact_info['contact_first_name'],
#             'billing_lastname': contact_info['contact_last_name'],
#             'billing_email': contact_info['contact_email'],
#             'description': "{inst} STARS Registration ({when})".format(
#                 inst=contact_info['contact_last_name'], when=datetime.now().isoformat()),
# #            'company': contact_info['name'],
#             'last_four': last_four,
#         }

#         if is_canadian_zipcode(pay_form.cleaned_data['billing_zipcode']):
#             payment_context['country'] = "Canada"

#         return payment_context

    def _process_payment(self,
                         card_num,
                         exp_date,
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
                'conf': "" }
        """
        # Assertions below help when debugging tests that fail because
        # settings.AUTHORIZENET_* aren't set.
        assert ((settings.AUTHORIZENET_SERVER is not None and
                 settings.AUTHORIZENET_LOGIN is not None and
                 settings.AUTHORIZENET_KEY is not None),
                'settings.AUTHORIZE_SERVER, settings.AUTHORIZE_LOGIN and '
                'settings.AUTHORIZE_KEY are required.')

        cc = CcProcessor(server=settings.AUTHORIZENET_SERVER,
                         login=settings.AUTHORIZENET_LOGIN,
                         key=settings.AUTHORIZENET_KEY)

        total = 0.0
        for product in products:
            total += product['price'] * product['quantity']

        result = cc.authorize(amount=str(total),
                              card_num=card_num,
                              exp_date=exp_date,
                              invoice_num=invoice_num)

        if result.response == "approved":
            capture_result = cc.captureAuthorized(trans_id=result.trans_id)
            return {'cleared': True,
                    'reason_code': None,
                    'msg': None,
                    'conf': capture_result.approval_code,
                    'trans_id': capture_result.trans_id}
        else:
            logger.error("Payment denied. %s" % result.response_reason)
            return {'cleared': False,
                    'reason_code': None,
                    'msg': result.response_reason,
                    'conf': None,
                    'trans_id': None}
