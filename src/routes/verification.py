from flask import Blueprint, request, jsonify
from datetime import datetime
import stripe
import os

# Import models
from src.models.user import db
from src.models.client import Client
from src.models.booking import Booking

verification_bp = Blueprint('verification', __name__)

# Stripe configuration - Use environment variables for production
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_51Rinj74ggsKDrnRRO6MyLv2VRHhHs3XBH9iX8iAgSX2KKwD4cUhKgKvZUgrcRcLC7QEqPUVNPRoHO7CnghKmy5Ea00sICS9j1r')

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
        
    except stripe.error.StripeError as e:
        print(f"❌ Stripe error: {str(e)}")
        return jsonify({'error': f'Stripe verification error: {str(e)}'}), 500
    except Exception as e:
        print(f"❌ Error creating verification session: {str(e)}")
        return jsonify({'error': 'Failed to create verification session'}), 500

@verification_bp.route('/api/verification/check-status', methods=['POST'])
def check_verification_status():
    """Check the status of a verification session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        
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
        
    except stripe.error.StripeError as e:
        print(f"Stripe error: {str(e)}")
        return jsonify({'error': 'Failed to check verification status'}), 500
    except Exception as e:
        print(f"Error checking verification status: {str(e)}")
        return jsonify({'error': 'Failed to check verification status'}), 500

@verification_bp.route('/api/verification/manual-approve', methods=['POST'])
def manual_approve_client():
    """Manually approve a client (admin only)"""
    try:
        data = request.get_json()
        client_id = data.get('client_id')
        admin_notes = data.get('admin_notes', '')
        
        if not client_id:
            return jsonify({'error': 'Client ID is required'}), 400
        
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        # Manually approve client
        client.is_verified = True
        client.verification_status = 'verified'
        client.verification_date = datetime.utcnow()
        client.verification_method = 'manual_approval'
        client.admin_notes = admin_notes
        
        db.session.commit()
        
        return jsonify({
            'message': 'Client manually approved',
            'client': client.to_dict()
        })
        
    except Exception as e:
        print(f"Error manually approving client: {str(e)}")
        return jsonify({'error': 'Failed to approve client'}), 500

@verification_bp.route('/api/clients', methods=['GET'])
def get_all_clients():
    """Get all clients for admin dashboard"""
    try:
        clients = Client.query.order_by(Client.created_at.desc()).all()
        return jsonify({
            'clients': [client.to_dict() for client in clients]
        })
        
    except Exception as e:
        print(f"Error fetching clients: {str(e)}")
        return jsonify({'error': 'Failed to fetch clients'}), 500

@verification_bp.route('/api/clients/<int:client_id>', methods=['GET'])
def get_client_details(client_id):
    """Get detailed client information"""
    try:
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        # Get client's booking history
        bookings = Booking.query.filter_by(client_id=client_id).order_by(Booking.created_at.desc()).all()
        
        return jsonify({
            'client': client.to_dict(),
            'bookings': [booking.to_dict() for booking in bookings]
        })
        
    except Exception as e:
        print(f"Error fetching client details: {str(e)}")
        return jsonify({'error': 'Failed to fetch client details'}), 500

@verification_bp.route('/api/clients/<int:client_id>/flag', methods=['POST'])
def flag_client(client_id):
    """Flag a client (admin only)"""
    try:
        data = request.get_json()
        flag_reason = data.get('flag_reason', '')
        
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        client.is_flagged = True
        client.flag_reason = flag_reason
        client.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Client flagged successfully',
            'client': client.to_dict()
        })
        
    except Exception as e:
        print(f"Error flagging client: {str(e)}")
        return jsonify({'error': 'Failed to flag client'}), 500

