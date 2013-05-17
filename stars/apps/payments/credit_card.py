from datetime import datetime
from logging import getLogger
import sys

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
                inst=contact_info['contact_last_name'], when=datetime.now().isoformat()),
#            'company': contact_info['name'],
            'last_four': last_four,
        }

        if is_canadian_zipcode(pay_form.cleaned_data['billing_zipcode']):
            payment_context['country'] = "Canada"

        return payment_context

    def _process_payment(self, payment_context, product_list,
                         invoice_num=None, server=None, login=None, key=None):
        """
            Connects to Authorize.net and processes a payment based on the
            payment information in payment_dict and the product_dict

            payment_dict: {first_name, last_name, street, city, state,
            zip, country, email, cc_number, expiration_date}

            product_list: [{'name': '', 'price': #.#, 'quantity': #},]

            server, login, and key: optional parameters for Auth.net
            connections (for testing)

            returns:
                {'cleared': cleared,
                'reason_code': reason_code,
                'msg': msg,
                'conf': "" }
        """
        if not server:
            server = settings.AUTHORIZENET_SERVER
            assert server is not None, "server is required"
        if not login:
            login = settings.AUTHORIZENET_LOGIN
            assert login is not None, "login is required"
        if not key:
            key = settings.AUTHORIZENET_KEY
            assert key is not None, "key is required"

        cc = CcProcessor(server=server, login=login, key=key)

        total = 0.0
        for product in product_list:
            total += product['price'] * product['quantity']
        result = cc.authorize(amount=str(total),
                              card_num=payment_context['cc_number'],
                              exp_date=payment_context['exp_date'],
                              invoice_num=invoice_num,
                              address=payment_context['billing_address'],
                              city=payment_context['billing_city'],
                              state=payment_context['billing_state'],
                              zip=payment_context['billing_zipcode'],
                              first_name=payment_context['billing_firstname'],
                              last_name=payment_context['billing_lastname'],
                              card_code=payment_context['cv_number'],
                              country=payment_context['country'])

        if result.response == "approved":
            capture_result = cc.captureAuthorized(trans_id=result.trans_id)
            return {'cleared': True,
                    'reason_code': None,
                    'msg': None,
                    'conf': capture_result.approval_code,
                    'trans_id': capture_result.trans_id}
        else:
            logger.error("Payment denied for %s %s (%s)" %
                           (payment_context['billing_firstname'],
                            payment_context['billing_lastname'],
                            result.response_reason))
            return {'cleared': False,
                    'reason_code': None,
                    'msg': result.response_reason,
                    'conf': None,
                    'trans_id': None}
