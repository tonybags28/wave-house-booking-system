from flask import Blueprint, request, jsonify
from datetime import datetime
import os

# Import models
from src.models.user import db
from src.models.client import Client
from src.models.booking import Booking

# Import stripe after other imports
try:
    import stripe
    print("✅ Stripe library imported successfully")
except ImportError as e:
    print(f"❌ Failed to import stripe: {e}")
    stripe = None

verification_bp = Blueprint('verification', __name__)

# Stripe configuration - Use environment variables for production
if stripe:
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_51Rinj74ggsKDrnRRO6MyLv2VRHhHs3XBH9iX8iAgSX2KKwD4cUhKgKvZUgrcRcLC7QEqPUVNPRoHO7CnghKmy5Ea00sICS9j1r')
    print(f"✅ Stripe API key configured: {stripe.api_key[:20]}...")
else:
    print("❌ Stripe not available")

@verification_bp.route('/api/verification/check-client', methods=['POST'])
def check_client_verification_status():
    """Check if a client exists and their verification status"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Check if client exists
        client = Client.query.filter_by(email=email).first()
        
        if not client:
            return jsonify({
                'client_exists': False,
                'is_verified': False,
                'needs_verification': True,
                'verification_status': 'new_client'
            })
        
        return jsonify({
            'client_exists': True,
            'is_verified': client.is_verified,
            'needs_verification': client.needs_verification(),
            'verification_status': client.verification_status,
            'total_bookings': client.total_bookings,
            'is_first_time': client.is_first_time_client()
        })
        
    except Exception as e:
        print(f"Error checking client verification: {str(e)}")
        return jsonify({'error': 'Failed to check client status'}), 500

@verification_bp.route('/api/verification/create-session', methods=['POST'])
def create_verification_session():
    """Create a Stripe Identity verification session"""
    try:
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        
        if not email or not name:
            return jsonify({'error': 'Email and name are required'}), 400
        
        print(f"🔐 Creating Stripe Identity verification session for {email}")
        
        # Check if stripe is available
        if not stripe:
            print("❌ Stripe library not available")
            return jsonify({'error': 'Verification service not available'}), 500
        
        # Debug stripe object
        print(f"🔍 Stripe object: {stripe}")
        print(f"🔍 Stripe version: {getattr(stripe, '__version__', 'unknown')}")
        print(f"🔍 Stripe identity: {getattr(stripe, 'identity', 'NOT FOUND')}")
        
        # Create or get client record
        client = Client.query.filter_by(email=email).first()
        if not client:
            client = Client(
                email=email,
                name=name,
                verification_status='pending'
            )
            db.session.add(client)
            db.session.commit()
            print(f"✅ Created new client record for {email}")
        
        # Test stripe connection first
        try:
            # Check if stripe.identity exists
            if not hasattr(stripe, 'identity'):
                print("❌ stripe.identity not found")
                return jsonify({'error': 'Stripe Identity not available in this version'}), 500
            
            if not hasattr(stripe.identity, 'VerificationSession'):
                print("❌ stripe.identity.VerificationSession not found")
                return jsonify({'error': 'VerificationSession not available'}), 500
            
            # Create Stripe Identity verification session
            verification_session = stripe.identity.VerificationSession.create(
                type='document',
                metadata={
                    'client_id': str(client.id),
                    'email': email
                },
                options={
                    'document': {
                        'allowed_types': ['driving_license', 'passport', 'id_card'],
                        'require_id_number': True,
                        'require_live_capture': True,
                        'require_matching_selfie': True,
                    }
                },
                return_url=f"https://honest-creativity-production.up.railway.app/verification/complete"
            )
            
            print(f"✅ Created Stripe verification session: {verification_session.id}")
            
            # Update client with verification session ID
            client.stripe_verification_session_id = verification_session.id
            client.verification_status = 'in_progress'
            db.session.commit()
            
            return jsonify({
                'verification_session_id': verification_session.id,
                'client_secret': verification_session.client_secret,
                'url': verification_session.url,
                'status': 'created'
            })
            
        except AttributeError as e:
            print(f"❌ Stripe AttributeError: {str(e)}")
            return jsonify({'error': f'Stripe configuration error: {str(e)}'}), 500
        except Exception as stripe_error:
            print(f"❌ Stripe API error: {str(stripe_error)}")
            return jsonify({'error': f'Stripe API error: {str(stripe_error)}'}), 500
        
    except Exception as e:
        print(f"❌ Error creating verification session: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to create verification session: {str(e)}'}), 500

@verification_bp.route('/api/verification/check-status', methods=['POST'])
def check_verification_status():
    """Check the status of a verification session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        
        if not stripe:
            return jsonify({'error': 'Stripe not available'}), 500
        
        # Retrieve verification session from Stripe
        verification_session = stripe.identity.VerificationSession.retrieve(session_id)
        
        # Find client by session ID
        client = Client.query.filter_by(stripe_verification_session_id=session_id).first()
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        # Update client based on verification status
        if verification_session.status == 'verified':
            client.is_verified = True
            client.verification_status = 'verified'
            client.verification_date = datetime.utcnow()
            client.verification_method = 'stripe_identity'
        elif verification_session.status == 'requires_input':
            client.verification_status = 'failed'
        elif verification_session.status == 'processing':
            client.verification_status = 'processing'
        
        db.session.commit()
        
        return jsonify({
            'status': verification_session.status,
            'client_verified': client.is_verified,
            'verification_status': client.verification_status
        })
        
    except Exception as e:
        print(f"Error checking verification status: {str(e)}")
        return jsonify({'error': 'Failed to check verification status'}), 500

