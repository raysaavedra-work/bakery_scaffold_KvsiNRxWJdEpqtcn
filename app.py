import json
import os
import stripe

from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
stripe.api_version = os.getenv('STRIPE_API_VERSION')

app = Flask(__name__, template_folder='client')


@app.route('/')
def order():
    return render_template('order.html')

@app.route('/order_success')
def success():
    return render_template('order_success.html')

@app.route('/failed')
def failed():
    return render_template('failed.html')

@app.route('/config', methods=['GET'])
def get_public_key():
    return jsonify({
      'publicKey': os.getenv('STRIPE_PUBLIC_KEY'),
      'basePrice': os.getenv('BASE_PRICE'),
      'currency': os.getenv('CURRENCY')
    })

# Fetch the Checkout Session to display the JSON result on the success page
@app.route('/checkout-session', methods=['GET'])
def get_checkout_session():
    id = request.args.get('sessionId')
    checkout_session = stripe.checkout.Session.retrieve(id)
    return jsonify(checkout_session)

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = json.loads(request.data)
    domain_url = os.getenv('DOMAIN')

    try:
        # Create new Checkout Session for the order
        # Other optional params include:
        # [billing_address_collection] - to display billing address details on the page
        # [customer] - if you have an existing Stripe Customer ID
        # [payment_intent_data] - lets capture the payment later
        # [customer_email] - lets you prefill the email input in the form
        # For full details see https:#stripe.com/docs/api/checkout/sessions/create
        
        # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url + "/order_success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url + "/failed",
            payment_method_types=["card"],
            line_items=[
                {
                    "name": "Pasha photo",
                    "images": ["https://picsum.photos/300/300?random=4"],
                    "quantity": data['quantity'],
                    "currency": os.getenv('CURRENCY'),
                    "amount": os.getenv('BASE_PRICE')
                }
            ]
        )
        return jsonify({'sessionId': checkout_session['id']})
    except Exception as e:
        return jsonify(e), 40


@app.route('/webhook', methods=['POST'])
def webhook_received():
    # You can use webhooks to receive information about asynchronous payment events.
    # For more about our webhook events check out https://stripe.com/docs/webhooks.
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    request_data = json.loads(request.data)

    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret)
            data = event['data']
        except Exception as e:
            return e
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
    else:
        data = request_data['data']
        event_type = request_data['type']
    data_object = data['object']
    print(data_object)
    print('event ' + event_type)

    if event_type == 'checkout.session.completed':
        print('🔔 Payment succeeded!')

    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run()