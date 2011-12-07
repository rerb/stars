"""
    Unittests for the registration process

    Test premises:
        - the forms are processed correctly
            - Select Institution Form
            - Contact Form
            - Payment Form
        - email notifications are sent
"""
from django.test import TestCase
from django.test.client import Client

import sys, os, random

class TestRules(TestCase):

    def setUp(self):
        pass
        
    def testRuleEngine(self):
        """
            Run the first step for international registration
        """
        from django.contrib.auth.models import User
        u = User(username='tester')
        u.set_password('tester')
        u.save()
        c = Client()
        c.login(username='tester', password='tester')

        url = '/rules/order_pizza/cheese/20/' 
        response = c.get(url)
        self.assertEqual(response.status_code, 404)

        url = '/rules/order_pizza/pepperoni/10/' 
        response = c.get(url)
        self.assertEqual(response.status_code, 404)

        url = '/rules/order_pizza/olives/10/' 
        response = c.get(url)
        self.assertEqual(response.status_code, 404)

        url = '/rules/order_pizza/cheese/10/' 
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
