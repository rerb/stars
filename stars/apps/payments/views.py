from abc import ABCMeta, abstractmethod

from django.contrib import messages
from django.contrib.formtools.wizard.views import SessionWizardView
from django.http import (HttpResponse,
                         HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.utils import simplejson as json

from . import forms
from ..institutions.models import Subscription, SubscriptionPurchaseError
from ..registration.models import (ExpiredDiscountCodeError,
                                   InvalidDiscountCodeError,
                                   NoActiveAutomaticDiscountError,
                                   get_automatic_discount,
                                   get_current_discount)

PAY_WHEN = 'pay_when'

SUCCESS, FAILURE = True, False


class SubscriptionPurchaseWizard(SessionWizardView):
    """SubscriptionPurchaseWizard walks the user through the process of
    paying for a subscription.

    Should be called SubscriptionCreateWizard.  Next changeset . . .

    There are three steps;

      0 - a view that displays the price of a subscription, and
          allows the user to enter a promo code;

      1 - a view that allows the user to specify payment options (now
          or later)

      2 - a view that creates a Subscription upon submission, and, if
          paying now, prompts the user for credit card info and
          processes a payment.

    Subclasses must provide implentations of two abstract methods;
    success_url() and get_institution().

    Base templates are provided in the TEMPLATES dict.  Copy, include,
    or extend them as the needs of your subclass dictate, then
    override get_template_names() accordingly.  Note that
    TEMPLATES[PRICE] is where the AJAX to apply promo codes lives.
    """
    __metaclass__ = ABCMeta

    PRICE, PAYMENT_OPTIONS, SUBSCRIPTION_CREATE = 0, 1, 2

    TEMPLATES = {
        PRICE: "payments/subscription_price.html",
        PAYMENT_OPTIONS: "payments/subscription_payment_options.html",
        SUBSCRIPTION_CREATE: "payments/subscription_payment_create.html"}

    FORMS = [(PRICE, forms.SubscriptionPriceForm),
             (PAYMENT_OPTIONS, forms.SubscriptionPaymentOptionsForm),
             (SUBSCRIPTION_CREATE, forms.DummySubscriptionCreateForm)]

    @classmethod
    def get_class_form_list(cls):
        return [form[1] for form in cls.FORMS]

    subscription_purchase_outcome = FAILURE  # safety in pessimism

    @property
    @abstractmethod
    def success_url(self):
        """Where to go at the end, after everything's OK!?"""
        raise NotImplementedError('subclass of SubscriptionPurchaseWizard '
                                  'must define success_url')

    @abstractmethod
    def get_institution(self):
        """Returns the institution in question (TIIQ) that we're talking about.
        """
        pass

    def get_template_names(self):
        return [self.TEMPLATES[int(self.steps.current)]]

    def post(self, *args, **kwargs):
        if self.request.is_ajax() and int(self.steps.current) == self.PRICE:
            form = self.get_form(data=self.request.POST)
            return self._process_step_price(form=form)
        else:
            return super(SubscriptionPurchaseWizard, self).post(*args,
                                                                **kwargs)

    def process_step(self, form):
        try:
            f = {self.PRICE: self._process_step_price,
                 self.PAYMENT_OPTIONS: self._process_step_payment_options,
                 self.SUBSCRIPTION_CREATE:
                 self._process_step_subscription_create}[
                     int(self.steps.current)]
        except KeyError:
            pass
        else:
            f(form)
        return super(SubscriptionPurchaseWizard, self).process_step(form)

    def get_context_data(self, form, **kwargs):
        context = super(SubscriptionPurchaseWizard, self).get_context_data(
            form, **kwargs)
        extra_context_methods = {
            self.PRICE: self._get_context_data_price,
            self.PAYMENT_OPTIONS: self._get_context_data_payment_options,
            self.SUBSCRIPTION_CREATE:
                self._get_context_data_subscription_create}

        current_step = int(self.steps.current)
        try:
            extra_context = extra_context_methods[current_step](form,
                                                                **kwargs)
        except KeyError:
            pass
        else:
            context.update(extra_context)

        return context

    def _get_automatic_discount(self):
        """Return the automatic ValueDiscount for this institution,
        if one is in effect.
        """
        try:
            return self._automatic_discount
        except AttributeError:
            try:
                self._automatic_discount = get_automatic_discount(
                    {'institution': self.get_institution(),
                     'Subscription': Subscription})
            except NoActiveAutomaticDiscountError:
                self._automatic_discount = None
        return self._automatic_discount

    def _get_context_data_price(self, form, **kwargs):
        context = {}

        (subscription_start_date, subscription_end_date) = (
            Subscription.get_date_range_for_new_subscription(
                self.get_institution()))

        context['subscription_start_date'] = subscription_start_date
        context['subscription_end_date'] = subscription_end_date

        institution = self.get_institution()

        prices = Subscription.get_prices_for_new_subscription(
            institution=institution)

        context['prices'] = prices

        context['institution_is_member'] = institution.is_member
        context['institution_name'] = institution.name
        
        context['join_aashe_url'] = 'http://www.aashe.org/membership'

        automatic_discount = self._get_automatic_discount()
        if automatic_discount:
            context['automatic_discount_code'] = automatic_discount.code

        return context

    ###################################################################
    # Automatic Discounts                                             #
    #                                                                 #
    # Effective date ranges of automatic discounts can't overlap,     #
    # so only one automatic ValueDiscount can be applicable at any    #
    # time.                                                           #
    #                                                                 #
    # Each automatic discount is applicable if today is in its        #
    # effective range, and its applicability filter is True.  An      #
    # applicability is a Python expression.  It can be as simple      #
    # as "True" so that the discount applies to all subscribers,      #
    # or more complicated, such as a discount that applies only       #
    # if a subscriber doesn't qualify for the early renewal           #
    # discount.                                                       #
    #                                                                 #
    # Applicability filters take two optional arguments, both         #
    # dictionaries.  The environment in which the filter expression   #
    # is evaluated is defined by adding `extra_globals` to globals(), #
    # and `extra_locals` to locals().  This allows you to provide     #
    # any objects the filter expression requires.                     #
    #                                                                 #
    # The pricing view determines if there's an automatic discount    #
    # that should be applied, and passes this determination to the    #
    # pricing template                                                #
    #                                                                 #
    # When an automatic discount is in effect, no other promo code    #
    # can be applied.                                                 #
    #                                                                 #
    # If an automatic discount should be applied, the template hides  #
    # the promo code widgets, and applies the discount code.          #
    #                                                                 #
    # Here's an example applicability filter that is true only        #
    # for those institutions that do not qualify for the              #
    # early renewal discount:                                         #
    #                                                                 #
    #   not globals()['Subscription'].create(                         #
    #       institution=globals(                                      #
    #       )['institution']).qualifies_for_early_renewal_discount()  #
    ###################################################################
    
    def _get_context_data_payment_options(self, form, **kwargs):
        context = {}
        context['amount_due'] = self.request.session['amount_due']
        return context

    def _get_context_data_subscription_create(self, form, **kwargs):
        context = {}
        # TODO: is this necessary? can a template resolve {{ var }}
        # to request.session[var]?
        context['amount_due'] = self.request.session['amount_due']
        context['pay_when'] = self.pay_when
        return context

    def _process_step_price(self, form):
        ajax_data = {}
        if self.request.is_ajax():
            promo_code_id = '_'.join(('id', form.add_prefix('promo_code')))
            promo_code = self.request.POST[promo_code_id]
        else:
            promo_code_name = form.add_prefix('promo_code')
            promo_code = self.request.POST[promo_code_name]
        try:
            ajax_data['prices'] = Subscription.get_prices_for_new_subscription(
                institution=self.get_institution(),
                promo_code=promo_code)
        except (ExpiredDiscountCodeError, InvalidDiscountCodeError) as exc:
            # promo code provided is invalid or expired, so throw it
            # away:
            promo_code = None
            # get the prices without a promo code:
            ajax_data['prices'] = Subscription.get_prices_for_new_subscription(
                institution=self.get_institution())
            if self.request.is_ajax():
                # send the error back to the caller:
                # TODO: isn't promo_code_id already calculated above?
                # why recalculate it here?
                promo_code_id = 'id_{step}-promo_code'.format(
                    step=self.steps.current)
                ajax_data['form-errors'] = {promo_code_id: exc.message}
                return HttpResponseBadRequest(json.dumps(ajax_data),
                                              mimetype='application/json')
        finally:
            # always store the promo_code and amount_due in the
            # session, exception or not, is_ajax() or not:
            self.request.session['promo_code'] = promo_code
            self.request.session['amount_due'] = ajax_data['prices']['total']

            if self.request.session['amount_due'] <= 0.00:
                # When the amount due is zero (e.g., when a 100%
                # discount code is used), the Payment Options view is
                # skipped, so self.request.session[PAY_WHEN] doesn't
                # get set.  Since pay_when is used to determine which
                # Subscription Create form to display (pay later or
                # pay now by credit card), we'll set pay_when to
                # PAY_LATER here -- this prevents asking for credit
                # card info when the subscription is free.
                self.request.session[PAY_WHEN] = Subscription.PAY_LATER

        if self.request.is_ajax():
            discount = get_current_discount(promo_code)
            if discount:
                discount_description = (
                    discount.description or 
                    # fake it
                    "Promo code {code} - {amount}".format(
                        code=discount.code,
                        amount=(discount.amount or
                                str(discount.percentage) + '%')))
                ajax_data.update(
                    {'discount_amount': discount.amount,
                     'discount_percentage': discount.percentage,
                     'discount_description': discount_description})
                return HttpResponse(json.dumps(ajax_data),
                                    mimetype='application/json')

    def _process_step_payment_options(self, form):
        # Pass on the payment option selected:
        self.request.session[PAY_WHEN] = form.cleaned_data[PAY_WHEN]

    def _process_step_subscription_create(self, form):
        """Purchases a subscription, and maybe takes a payment for it."""
        if self.pay_when == Subscription.PAY_NOW:
            card_num = form.cleaned_data['card_number']
            exp_date = self.get_exp_date(form)
        else:
            card_num = None
            exp_date = None

        promo_code = self.request.session.get('promo_code')

        just_created_an_institution = False

        institution = self.get_institution()
        if not institution.pk:
            just_created_an_institution = True
            institution.save()

        try:
            subscription = Subscription.purchase(
                institution=institution,
                pay_when=self.pay_when,
                user=self.request.user,
                promo_code=promo_code,
                card_num=card_num,
                exp_date=exp_date)
        except SubscriptionPurchaseError as spe:
            messages.error(self.request, str(spe))
            self.subscription_purchase_outcome = FAILURE
            if just_created_an_institution:
                institution.delete()
        except Exception:
            if just_created_an_institution:
                institution.delete()
            raise
        else:
            self.subscription_purchase_outcome = SUCCESS
            messages.info(self.request,
                          """Thank you!
                          Your new subscription lasts from
                          {start} to {finish}.""".format(
                              start=subscription.start_date,
                              finish=subscription.end_date))

    def get_exp_date(self, form):
        """
            Returns the expiration date from `form`, in the format
            the credit card processor expects, a string of 'MMYYYY'.
        """
        exp_date_month = form.cleaned_data['exp_month']
        exp_date_year = form.cleaned_data['exp_year']
        exp_date = exp_date_month + exp_date_year
        return exp_date

    @property
    def pay_when(self):
        """Just a shorthand for self.request.session[PAY_WHEN]."""
        return self.request.session[PAY_WHEN]

    def render_done(self, form, **kwargs):
        """Oh, this is ugly, but we don't know for sure which form
        is the last one when we get here.  self.forms_list is conditioned
        by get_form_conditions, and the list could get manually poked
        elsewhere, so though the last form of this wizard is *probably*
        *usually* the one that creates a subscription, it might not be.

        When it is, we want to move along if it a Subscription was purchased
        successfully, and bounce back if there was an error.

        When the last form isn't the subscription create form, we'll
        just pass along.  (This happens in the RegistrationWizard when
        registrants choose to be survey responders rather than paying
        STARS participants.)
        """
        if isinstance(form, self.form_list[str(self.SUBSCRIPTION_CREATE)]):
            if self.subscription_purchase_outcome == SUCCESS:
                return super(SubscriptionPurchaseWizard, self).render_done(
                    form, **kwargs)
            else:
                return self.render(
                    form,
                    initial_dict={
                        str(self.SUBSCRIPTION_CREATE): form.cleaned_data})
        else:
            return super(SubscriptionPurchaseWizard, self).render_done(
                form, **kwargs)

    def done(self, forms, **kwargs):
        return HttpResponseRedirect(self.success_url)

    def get_form(self, step=None, data=None, files=None):
        if step is None:
            step = self.steps.current
        if int(step) == self.SUBSCRIPTION_CREATE:
            correct_pay_when_form = {
                Subscription.PAY_LATER: forms.SubscriptionPayLaterForm,
                Subscription.PAY_NOW: forms.SubscriptionPayNowForm}[
                    self.pay_when]
            self.form_list[str(self.SUBSCRIPTION_CREATE)] = (
                correct_pay_when_form)
        return super(SubscriptionPurchaseWizard, self).get_form(step,
                                                                data,
                                                                files)

    @classmethod
    def insert_forms_into_form_list(cls, forms):
        # TODO: this method should increase PRICE, PAYMENT_OPTIONS, and
        # SUBSCRIPTION_CREATE by len(forms), too.
        return forms + cls.FORMS

    @classmethod
    def get_form_conditions(cls):
        return {str(cls.PAYMENT_OPTIONS): amount_due_more_than_zero}


def amount_due_more_than_zero(wizard):
    """Pulls the amount due from the request session, if it's there, and
    returns True if it's greater than 0.00.  Otherwise, returns False.

    For use in SubscriptionPurchaseWizard constructor, in the
    condition_dict argument, to determine if the payment options
    form should be shown.  (Don't want to show it if the amount
    due is 0.00).

    Usage:

        from django.conf.urls import patterns

        from payments.views import (amount_due_more_than_zero,
                                    SubscriptionPurchaseWizard)

        urlpatterns = patterns('',
            (r'^contact/$', SubscriptionPurchaseWizard.as_view(
                SubscriptionPurchaseWizard.FORM_LIST,
                condition_dict={
                    str(SubscriptionPurchaseWizard.PAYMENT_OPTIONS):
                    amount_due_more_than_zero})))

    Or, use get_form_conditions() defined above:

        urlpatterns = patterns('',
            (r'^contact/$', SubscriptionPurchaseWizard.as_view(
                SubscriptionPurchaseWizard.FORM_LIST,
                condition_dict=SubscriptionPurchaseWizard.get_form_conditions()
         )))
    """
    return wizard.request.session.get('amount_due', 0.00) > 0.00
