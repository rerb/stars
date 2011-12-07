# Rule Definitions
# Will probably use the Register pattern to get
# the rules stored... similar to the Django Admin
# but this simulation works for now

from django.views.generic.base import TemplateView, TemplateResponseMixin
from django.http import HttpResponseNotFound

import sys

def can_make_pizza(pizza_place, topping):
    if topping in pizza_place.inventory_list:
        return True
    print >> sys.stderr, "Can't make %s pizza!" % topping
    return False

def can_afford_pizza(user, charge):
    if int(charge) < 20:
        return True
    print >> sys.stderr, "Can't afford $%s pizza!" % charge
    return False

def can_order_pizza(user, pizza_topping, charge):
    """
    A user can order a pizza if they can afford it
    and they like the selected topping
    """
    if can_afford_pizza(user, charge):
        if pizza_topping != "pepperoni" and user.username == 'tester':
            return True
        else:
            print >> sys.stderr, "Doesn't like pizza"
    return False

RULES = {
    "can_make_pizza": can_make_pizza,
    "can_afford_pizza": can_afford_pizza,
    "can_order_pizza": can_order_pizza,
    }

def test_rule(rule_name, *args):
    """
    Method to run rules
    """
    print >> sys.stderr, "running rule: %s" % rule_name
    rule = RULES[rule_name]
    return rule(*args)

class RuleTester():
    """
    A RuleTester is used to have prerequisite Rules for views

    It stores the rule and knows how to get the parameters from the context or
    the view class' callback method
    """
    def __init__(self, rule_name, context_keys, response_callback, param_callback=None, requires_user=True):
        self.rule_name = rule_name
        self.context_keys = context_keys
        self.response_callback = response_callback
        self.param_callback = param_callback
        self.requires_user = requires_user

    def test(self, instance, user, context):
        """
        Runs the rule using the context or the callback to get the parameters
        The instance is the view instance with the callback methods
        """
        args = []
        if self.requires_user:
            # @side-effect: Forces all rules to take the user as an argument
            # as the first parameter :(
            args = [user,]
        if self.param_callback:
            callback = getattr(instance, self.param_callback)
            args += callback(context)
        else:
            for key in self.context_keys:
                args.append(context[key])
        
        return test_rule(self.rule_name, *args)

class RuleMixin(TemplateResponseMixin):

    def render_to_response(self, context, **response_kwargs):
        for r in self.rule_list:
            if not r.test(self, self.request.user, context):
                return r.response_callback()
        return super(RuleMixin, self).render_to_response(context)
        
    def param_callback(self):
        """
        Methods like this can be used to provide params for specific rules
        """
        raise NotImplementedError, "Make your own!"
    
class OrderPizzaView(TemplateView, RuleMixin):
    """
    A test class for the RuleMixin view

    Two rules with one using the context (from the URL params)
    and one using a specific callback
    """
    template_name = "rules/test.html"

    rule_list = [
        RuleTester("can_make_pizza", [], HttpResponseNotFound, param_callback="get_pizza_place_params", requires_user=False),
        RuleTester("can_order_pizza", ["topping",  "charge"], HttpResponseNotFound),
        ]
    
    def get_context_data(self, **kwargs):
        return kwargs

    def get_pizza_place_params(self, context):
        d = []
        class PizzaPlace():
            def __init__(self, inventory):
                self.inventory_list = inventory
        d.append(PizzaPlace(['cheese', 'pepperoni']))
        d.append(context['topping'])

        return d

"""
Things to decide:

rules are classes or methods?

"""
