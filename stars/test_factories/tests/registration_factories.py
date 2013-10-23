import unittest

from stars.test_factories import registration_factories


class ValueDiscountFactoryTest(unittest.TestCase):

    def test_value_discount_code_is_unique(self):
        """Is code for ValueDiscount unique?"""
        first_value_discount = registration_factories.ValueDiscountFactory()
        second_value_discount = registration_factories.ValueDiscountFactory()
        self.assertNotEqual(first_value_discount.code,
                            second_value_discount.code)
        
