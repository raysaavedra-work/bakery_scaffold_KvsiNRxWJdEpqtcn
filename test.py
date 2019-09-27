import re
import unittest


class TestAcceptanceStripe(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestAcceptanceStripe, self).__init__(*args, **kwargs)
        with open('order.html', 'r') as file_descriptor:
            self.dom_str = file_descriptor.read()

    def test_acceptance_stripe_public_key_has_been_set(self):
        """Check if Stripe key was defined."""
        pattern = re.compile(r"Stripe\('pk_test_\w+'\);", re.I | re.M)
        res = re.search(pattern, self.dom_str)
        self.assertTrue(hasattr(res, 'group'), msg="You didn't define the Stripe key.")

    def test_acceptance_stripe_script_has_been_inserted(self):
        """Check if Stripe script was inserted."""
        pattern = re.compile(r'<script src="https://js.stripe.com/v3"></script>',
                             re.I | re.M)
        res = re.search(pattern, self.dom_str)
        self.assertTrue(hasattr(res, 'group'),
                        msg="You didn't insert a Stripe script file.")

    def test_acceptance_checkout_button_was_instantiated(self):
        """Check if checkout button was captured."""
        pattern = re.compile(
            r"document.getElementById\('checkout-button-sku_\w{14}'\);", re.I | re.M)
        res = re.search(pattern, self.dom_str)
        self.assertTrue(hasattr(res, 'group'),
                        msg="You didn't add a checkout button.")

    def test_acceptance_sku_item_defined_on_checkout(self):
        """Check if checkout button was captured."""
        pattern = re.compile(r"items: \[\{sku: 'sku_\w{14}', quantity: \d{1}\}\]",
                             re.I | re.M)
        res = re.search(pattern, self.dom_str)
        self.assertTrue(hasattr(res, 'group'),
                        msg="You didn't add the SKU code in the items list.")

    # Check if redirectToCheckout function call is present
    def test_acceptance_redirect_to_checkout(self):
        pattern = re.compile(r"stripe.redirectToCheckout", re.I | re.M)
        res = re.search(pattern, self.dom_str)
        self.assertTrue(hasattr(res, 'group'), msg="No checkout redirection was found.")

    # Check if successUrl redirects to order_success.html
    def test_acceptance_success_url(self):
        pattern = re.compile(
            r"successUrl: \'(http|https)://(.*)/order_success.html\?session_id=\{CHECKOUT_SESSION_ID\}\'",
            re.I | re.M)
        res = re.search(pattern, self.dom_str)
        self.assertTrue(hasattr(res, 'group'), msg="You didn't define a success URL.")

    # Check if cancelUrl redirects to order.html
    def test_acceptance_cancel_url(self):
        pattern = re.compile(r"cancelUrl: \'(http|https)://(.*)/order.html\'",
                             re.I | re.M)
        res = re.search(pattern, self.dom_str)
        self.assertTrue(hasattr(res, 'group'), msg="You didn't define a cancel URL.")


if __name__ == '__main__':
    unittest.main()
