from flask import Blueprint, request, jsonify, render_template_string
from src.models.user import db
from src.models.booking import Booking
from flask_cors import cross_origin
import json

payment_bp = Blueprint('payment', __name__)

# Payment integration explanation page
PAYMENT_EXPLANATION = """
<!DOCTYPE html>
<html>
<head>
    <title>Wave House - Payment Integration Guide</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: white; line-height: 1.6; }
        .container { max-width: 1000px; margin: 0 auto; }
        .option { background: #2a2a2a; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #00ffff; }
        .pros { color: #00ff00; }
        .cons { color: #ff6666; }
        h1, h2 { color: #00ffff; }
        code { background: #333; padding: 2px 6px; border-radius: 3px; }
        .example { background: #333; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .step { background: #2a2a2a; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 3px solid #ffa500; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Wave House Payment Integration Options</h1>
        
        <h2>Current Booking Flow</h2>
        <div class="step">
            <h3>Step 1: Booking Request</h3>
            <p>Customer submits booking request → Status: "pending"</p>
        </div>
        <div class="step">
            <h3>Step 2: Admin Review</h3>
            <p>You review and confirm booking → Status: "confirmed"</p>
        </div>
        <div class="step">
            <h3>Step 3: Payment Collection</h3>
            <p><strong>This is where payment integration comes in!</strong></p>
        </div>

        <h2>Payment Integration Options</h2>

        <div class="option">
            <h3>Option 1: Stripe Integration (Recommended)</h3>
            <p><strong>Best for:</strong> Professional online payments, automatic processing</p>
            
            <h4 class="pros">✅ Pros:</h4>
            <ul>
                <li>Industry standard, trusted by customers</li>
                <li>Automatic payment processing</li>
                <li>Handles deposits and full payments</li>
                <li>Built-in fraud protection</li>
                <li>Easy refund management</li>
                <li>Mobile-friendly checkout</li>
            </ul>
            
            <h4 class="cons">❌ Cons:</h4>
            <ul>
                <li>2.9% + 30¢ per transaction fee</li>
                <li>Requires business verification</li>
                <li>More complex setup</li>
            </ul>

            <h4>Implementation:</h4>
            <div class="example">
                <p>1. Create Stripe account at stripe.com</p>
                <p>2. Get API keys (publishable and secret)</p>
                <p>3. Add Stripe checkout to booking flow</p>
                <p>4. Set up webhooks for payment confirmation</p>
            </div>
        </div>

        <div class="option">
            <h3>Option 2: PayPal Integration</h3>
            <p><strong>Best for:</strong> Customers who prefer PayPal, international payments</p>
            
            <h4 class="pros">✅ Pros:</h4>
            <ul>
                <li>Widely recognized and trusted</li>
                <li>Good for international customers</li>
                <li>Buyer protection</li>
                <li>Easy setup</li>
            </ul>
            
            <h4 class="cons">❌ Cons:</h4>
            <li>Similar fees to Stripe</li>
            <li>Less modern checkout experience</li>
            <li>More redirects in payment flow</li>
        </div>

        <div class="option">
            <h3>Option 3: Manual Payment Processing</h3>
            <p><strong>Best for:</strong> Starting simple, personal relationships</p>
            
            <h4 class="pros">✅ Pros:</h4>
            <ul>
                <li>No transaction fees</li>
                <li>Full control over process</li>
                <li>Can accept multiple payment methods</li>
                <li>Personal touch</li>
            </ul>
            
            <h4 class="cons">❌ Cons:</h4>
            <ul>
                <li>Manual work for each booking</li>
                <li>No automatic confirmation</li>
                <li>Requires trust from customers</li>
                <li>More admin work</li>
            </ul>

            <h4>Current Implementation:</h4>
            <div class="example">
                <p>✅ Booking requests are collected</p>
                <p>✅ Admin dashboard to manage bookings</p>
                <p>📧 Send payment instructions via email: <strong>letswork@wavehousela.com</strong></p>
                <p>💳 Accept Venmo, Zelle, bank transfer, etc.</p>
                <p>✅ Manually confirm when payment received</p>
            </div>
        </div>

        <div class="option">
            <h3>Option 4: Hybrid Approach (Recommended for Starting)</h3>
            <p><strong>Best for:</strong> Gradual transition to automated payments</p>
            
            <h4>Phase 1: Manual (Current)</h4>
            <ul>
                <li>Use current booking system</li>
                <li>Collect payments manually</li>
                <li>Build customer base</li>
            </ul>
            
            <h4>Phase 2: Add Stripe</h4>
            <ul>
                <li>Integrate Stripe for deposits</li>
                <li>Collect balance manually or via Stripe</li>
                <li>Offer both options to customers</li>
            </ul>
        </div>

        <h2>Recommended Next Steps</h2>
        <div class="step">
            <h3>Immediate (This Week)</h3>
            <p>✅ Use current system with manual payments</p>
            <p>📧 Create email templates for payment instructions (send to: <strong>letswork@wavehousela.com</strong>)</p>
            <p>💰 Set up Venmo/Zelle for easy payments</p>
        </div>
        
        <div class="step">
            <h3>Short Term (Next Month)</h3>
            <p>🔧 Add Stripe integration for deposits</p>
            <p>📱 Create mobile-friendly payment flow</p>
            <p>🔄 Automate confirmation emails</p>
        </div>

        <h2>Testing Your Current System</h2>
        <div class="example">
            <p><strong>Admin Dashboard:</strong> <a href="/admin" style="color: #00ffff;">https://zmhqivcgp501.manus.space/admin</a></p>
            <p><strong>Main Website:</strong> <a href="/" style="color: #00ffff;">https://zmhqivcgp501.manus.space</a></p>
            <p><strong>How to test double-booking prevention:</strong></p>
            <ol>
                <li>Make a booking for a specific time</li>
                <li>Go to admin dashboard and confirm it</li>
                <li>Try to book overlapping time - should be blocked!</li>
            </ol>
        </div>
    </div>
</body>
</html>
"""

@payment_bp.route('/payment-guide')
def payment_guide():
    return render_template_string(PAYMENT_EXPLANATION)

# Stripe integration example (commented out - requires Stripe account)
"""
import stripe

@payment_bp.route('/create-payment-intent', methods=['POST'])
@cross_origin()
def create_payment_intent():
    try:
        data = request.get_json()
        booking_id = data.get('booking_id')
        amount = data.get('amount')  # in cents
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            metadata={'booking_id': booking_id}
        )
        
        return jsonify({
            'client_secret': intent.client_secret
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, 'your_webhook_secret'
        )
        
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            booking_id = payment_intent['metadata']['booking_id']
            
            # Update booking status
            booking = Booking.query.get(booking_id)
            if booking:
                booking.status = 'confirmed'
                booking.payment_status = 'paid'
                db.session.commit()
        
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
"""

