from flask import Blueprint, request, jsonify, render_template_string, session
from src.models.user import db
from src.models.booking import Booking, BlockedSlot
from flask_cors import cross_origin

admin_bp = Blueprint('admin', __name__)

# Admin password - change this to something secure
ADMIN_PASSWORD = "admin123"

# Login form template
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Wave House Admin - Login</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: #1a1a1a; 
            color: white; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            margin: 0; 
        }
        .login-container { 
            background: #2a2a2a; 
            padding: 40px; 
            border-radius: 12px; 
            text-align: center; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            max-width: 400px;
            width: 100%;
        }
        .logo { 
            color: #00ffff; 
            font-size: 24px; 
            margin-bottom: 30px; 
            font-weight: bold;
        }
        input[type="password"] { 
            width: 100%; 
            padding: 15px; 
            margin: 15px 0; 
            border: 1px solid #555; 
            border-radius: 6px; 
            background: #333; 
            color: white; 
            font-size: 16px;
            box-sizing: border-box;
        }
        input[type="password"]:focus {
            outline: none;
            border-color: #00ffff;
        }
        button { 
            width: 100%;
            padding: 15px; 
            background: #00aa00; 
            color: white; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            font-size: 16px;
            font-weight: bold;
        }
        button:hover { 
            background: #00cc00; 
        }
        .error { 
            color: #ff4444; 
            margin-top: 15px; 
        }
        .subtitle {
            color: #aaa;
            margin-bottom: 30px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">🎵 Wave House</div>
        <div class="subtitle">Admin Dashboard</div>
        <form method="POST">
            <input type="password" name="password" placeholder="Enter admin password" required autofocus>
            <button type="submit">Access Dashboard</button>
        </form>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

# Simple admin interface HTML template
ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Wave House Admin</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: white; }
        .container { max-width: 1200px; margin: 0 auto; }
        .booking { background: #2a2a2a; padding: 15px; margin: 10px 0; border-radius: 8px; }
        .booking.pending { border-left: 4px solid #ffa500; }
        .booking.confirmed { border-left: 4px solid #00ff00; }
        .booking.cancelled { border-left: 4px solid #ff0000; }
        button { padding: 8px 16px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; }
        .confirm { background: #00aa00; color: white; }
        .cancel { background: #aa0000; color: white; }
        .delete { background: #666; color: white; }
        h1, h2 { color: #00ffff; }
        .stats { display: flex; gap: 20px; margin: 20px 0; }
        .stat { background: #333; padding: 15px; border-radius: 8px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Wave House Admin Dashboard</h1>
        
        <div class="stats">
            <div class="stat">
                <h3>Total Bookings</h3>
                <p id="total-bookings">{{ total_bookings }}</p>
            </div>
            <div class="stat">
                <h3>Pending</h3>
                <p id="pending-bookings">{{ pending_bookings }}</p>
            </div>
            <div class="stat">
                <h3>Confirmed</h3>
                <p id="confirmed-bookings">{{ confirmed_bookings }}</p>
            </div>
        </div>

        <h2>Booking Requests</h2>
        <div id="bookings">
            {% for booking in bookings %}
            <div class="booking {{ booking.status }}" id="booking-{{ booking.id }}">
                <h3>{{ booking.name }} - {{ booking.service_type }}</h3>
                <p><strong>Date:</strong> {{ booking.date }} at {{ booking.time }}</p>
                <p><strong>Duration:</strong> {{ booking.duration or 'N/A' }}</p>
                <p><strong>Email:</strong> {{ booking.email }}</p>
                <p><strong>Phone:</strong> {{ booking.phone or 'N/A' }}</p>
                <p><strong>Project:</strong> {{ booking.project_type or 'N/A' }}</p>
                <p><strong>Message:</strong> {{ booking.message or 'N/A' }}</p>
                <p><strong>Status:</strong> {{ booking.status }}</p>
                <p><strong>Created:</strong> {{ booking.created_at }}</p>
                
                {% if booking.status == 'pending' %}
                <button class="confirm" onclick="updateStatus({{ booking.id }}, 'confirmed')">Confirm Booking</button>
                <button class="cancel" onclick="updateStatus({{ booking.id }}, 'cancelled')">Cancel Booking</button>
                {% endif %}
                <button class="delete" onclick="deleteBooking({{ booking.id }})">Delete</button>
            </div>
            {% endfor %}
        </div>
    </div>

    <script>
        function updateStatus(bookingId, status) {
            fetch(`/admin/bookings/${bookingId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: status })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Error: ' + data.error);
                } else {
                    location.reload();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error updating booking');
            });
        }

        function deleteBooking(bookingId) {
            if (confirm('Are you sure you want to delete this booking?')) {
                fetch(`/admin/bookings/${bookingId}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert('Error: ' + data.error);
                    } else {
                        location.reload();
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error deleting booking');
                });
            }
        }
    </script>
</body>
</html>
"""

@admin_bp.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        # Handle login
        password = request.form.get('password')
        print(f"DEBUG: Received password: '{password}'")
        print(f"DEBUG: Expected password: '{ADMIN_PASSWORD}'")
        print(f"DEBUG: Password match: {password == ADMIN_PASSWORD}")
        
        if password and password.strip() == ADMIN_PASSWORD:
            session['admin_authenticated'] = True
            print("DEBUG: Authentication successful")
            # Redirect to dashboard after successful login
            return admin_dashboard_view()
        else:
            print("DEBUG: Authentication failed")
            return render_template_string(LOGIN_TEMPLATE, error="Incorrect password")
    
    # Check if already authenticated
    if session.get('admin_authenticated'):
        return admin_dashboard_view()
    
    # Show login form
    return render_template_string(LOGIN_TEMPLATE)

def admin_dashboard_view():
    """Display the actual admin dashboard"""
    try:
        bookings = Booking.query.order_by(Booking.created_at.desc()).all()
        
        total_bookings = len(bookings)
        pending_bookings = len([b for b in bookings if b.status == 'pending'])
        confirmed_bookings = len([b for b in bookings if b.status == 'confirmed'])
        
        return render_template_string(ADMIN_TEMPLATE, 
                                    bookings=bookings,
                                    total_bookings=total_bookings,
                                    pending_bookings=pending_bookings,
                                    confirmed_bookings=confirmed_bookings)
    except Exception as e:
        return f"Error: {str(e)}", 500

@admin_bp.route('/admin/logout')
def admin_logout():
    """Logout from admin dashboard"""
    session.pop('admin_authenticated', None)
    return render_template_string(LOGIN_TEMPLATE, error="Logged out successfully")

@admin_bp.route('/admin/bookings/<int:booking_id>', methods=['PUT'])
@cross_origin()
def update_booking_admin(booking_id):
    try:
        data = request.get_json()
        booking = Booking.query.get_or_404(booking_id)
        
        if 'status' in data:
            booking.status = data['status']
        
        db.session.commit()
        return jsonify({'message': 'Booking updated successfully', 'booking': booking.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/bookings/<int:booking_id>', methods=['DELETE'])
@cross_origin()
def delete_booking_admin(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        db.session.delete(booking)
        db.session.commit()
        
        return jsonify({'message': 'Booking deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

