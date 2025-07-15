from flask import Blueprint, request, jsonify, render_template_string, session
from src.models.user import db
from src.models.booking import Booking, BlockedSlot
from flask_cors import cross_origin
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# Simple test route to verify blueprint is working
@admin_bp.route('/admin/test')
def admin_test():
    return "Admin blueprint is working!"

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
        .blocked-slot { background: #3a2a2a; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #ff6600; }
        button { padding: 8px 16px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; }
        .confirm { background: #00aa00; color: white; }
        .cancel { background: #aa0000; color: white; }
        .delete { background: #666; color: white; }
        .block-btn { background: #ff6600; color: white; }
        h1, h2 { color: #00ffff; }
        .stats { display: flex; gap: 20px; margin: 20px 0; }
        .stat { background: #333; padding: 15px; border-radius: 8px; text-align: center; }
        .bulk-block-form { background: #2a2a2a; padding: 20px; margin: 20px 0; border-radius: 8px; }
        .form-group { margin: 15px 0; }
        .form-group label { display: block; margin-bottom: 5px; color: #00ffff; }
        .form-group input, .form-group select, .form-group textarea { 
            width: 100%; padding: 10px; border: 1px solid #555; border-radius: 4px; 
            background: #333; color: white; box-sizing: border-box; 
        }
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: none; border-color: #00ffff;
        }
        .time-slots { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; margin: 10px 0; }
        .time-slot { background: #333; padding: 8px; border-radius: 4px; text-align: center; cursor: pointer; border: 2px solid transparent; }
        .time-slot:hover { border-color: #00ffff; }
        .time-slot.selected { background: #ff6600; border-color: #ff6600; }
        .tabs { display: flex; margin: 20px 0; }
        .tab { padding: 10px 20px; background: #333; border: none; color: white; cursor: pointer; margin-right: 5px; border-radius: 4px 4px 0 0; }
        .tab.active { background: #00ffff; color: #1a1a1a; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
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
            <div class="stat">
                <h3>Blocked Slots</h3>
                <p id="blocked-slots">{{ blocked_slots_count }}</p>
            </div>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="showTab('bookings')">Booking Requests</button>
            <button class="tab" onclick="showTab('blocking')">Bulk Block Times</button>
            <button class="tab" onclick="showTab('blocked-slots')">Manage Blocked Slots</button>
        </div>

        <div id="bookings" class="tab-content active">
            <h2>Booking Requests</h2>
            <div id="bookings-list">
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

        <div id="blocking" class="tab-content">
            <h2>Bulk Block Time Slots</h2>
            <div class="bulk-block-form">
                <form id="bulk-block-form">
                    <div class="form-group">
                        <label for="start-date">Start Date:</label>
                        <input type="date" id="start-date" name="start_date" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="end-date">End Date:</label>
                        <input type="date" id="end-date" name="end_date" required>
                    </div>
                    
                    <div class="form-group">
                        <label>Select Days of Week:</label>
                        <div style="display: flex; gap: 10px; margin: 10px 0;">
                            <label><input type="checkbox" name="days" value="0" checked> Sunday</label>
                            <label><input type="checkbox" name="days" value="1" checked> Monday</label>
                            <label><input type="checkbox" name="days" value="2" checked> Tuesday</label>
                            <label><input type="checkbox" name="days" value="3" checked> Wednesday</label>
                            <label><input type="checkbox" name="days" value="4" checked> Thursday</label>
                            <label><input type="checkbox" name="days" value="5" checked> Friday</label>
                            <label><input type="checkbox" name="days" value="6" checked> Saturday</label>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Select Time Slots to Block:</label>
                        <div class="time-slots" id="time-slots">
                            <!-- Time slots will be generated by JavaScript -->
                        </div>
                        <button type="button" onclick="selectAllTimes()">Select All</button>
                        <button type="button" onclick="selectNightHours()">Select Night Hours (10PM-6AM)</button>
                        <button type="button" onclick="clearTimeSelection()">Clear Selection</button>
                    </div>
                    
                    <div class="form-group">
                        <label for="reason">Reason for Blocking:</label>
                        <input type="text" id="reason" name="reason" placeholder="e.g., Monthly client rental, Maintenance, Holiday" required>
                    </div>
                    
                    <button type="submit" class="block-btn">Block Selected Time Slots</button>
                </form>
            </div>
        </div>

        <div id="blocked-slots" class="tab-content">
            <h2>Manage Blocked Slots</h2>
            <div id="blocked-slots-list">
                {% for slot in blocked_slots %}
                <div class="blocked-slot" id="blocked-slot-{{ slot.id }}">
                    <h3>{{ slot.date }} at {{ slot.time }}</h3>
                    <p><strong>Reason:</strong> {{ slot.reason or 'No reason specified' }}</p>
                    <p><strong>Created:</strong> {{ slot.created_at }}</p>
                    <button class="delete" onclick="deleteBlockedSlot({{ slot.id }})">Remove Block</button>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

    <script>
        // Tab functionality
        function showTab(tabName) {
            // Hide all tab contents
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Remove active class from all tabs
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
        }

        // Generate time slots
        function generateTimeSlots() {
            const timeSlotsContainer = document.getElementById('time-slots');
            const times = [];
            
            // Generate 24-hour time slots
            for (let hour = 0; hour < 24; hour++) {
                const time12 = hour === 0 ? '12:00 AM' : 
                              hour < 12 ? `${hour}:00 AM` : 
                              hour === 12 ? '12:00 PM' : 
                              `${hour - 12}:00 PM`;
                const time24 = `${hour.toString().padStart(2, '0')}:00`;
                times.push({ display: time12, value: time24 });
            }
            
            times.forEach(time => {
                const slot = document.createElement('div');
                slot.className = 'time-slot';
                slot.textContent = time.display;
                slot.dataset.time = time.value;
                slot.onclick = () => toggleTimeSlot(slot);
                timeSlotsContainer.appendChild(slot);
            });
        }

        function toggleTimeSlot(slot) {
            slot.classList.toggle('selected');
        }

        function selectAllTimes() {
            const slots = document.querySelectorAll('.time-slot');
            slots.forEach(slot => slot.classList.add('selected'));
        }

        function selectNightHours() {
            clearTimeSelection();
            const slots = document.querySelectorAll('.time-slot');
            slots.forEach(slot => {
                const hour = parseInt(slot.dataset.time.split(':')[0]);
                if (hour >= 22 || hour < 6) { // 10PM to 6AM
                    slot.classList.add('selected');
                }
            });
        }

        function clearTimeSelection() {
            const slots = document.querySelectorAll('.time-slot');
            slots.forEach(slot => slot.classList.remove('selected'));
        }

        // Form submission
        document.getElementById('bulk-block-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const selectedTimes = Array.from(document.querySelectorAll('.time-slot.selected'))
                                      .map(slot => slot.dataset.time);
            const selectedDays = Array.from(document.querySelectorAll('input[name="days"]:checked'))
                                     .map(input => parseInt(input.value));
            
            if (selectedTimes.length === 0) {
                alert('Please select at least one time slot to block.');
                return;
            }
            
            if (selectedDays.length === 0) {
                alert('Please select at least one day of the week.');
                return;
            }
            
            const data = {
                start_date: formData.get('start_date'),
                end_date: formData.get('end_date'),
                days: selectedDays,
                times: selectedTimes,
                reason: formData.get('reason')
            };
            
            fetch('/admin/bulk-block', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Error: ' + data.error);
                } else {
                    alert(`Successfully blocked ${data.blocked_count} time slots!`);
                    location.reload();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error blocking time slots');
            });
        });

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

        function deleteBlockedSlot(slotId) {
            if (confirm('Are you sure you want to remove this blocked time slot?')) {
                fetch(`/admin/blocked-slots/${slotId}`, {
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
                    alert('Error deleting blocked slot');
                });
            }
        }

        // Initialize time slots when page loads
        document.addEventListener('DOMContentLoaded', function() {
            generateTimeSlots();
            
            // Set default dates (today and 3 months from now)
            const today = new Date();
            const threeMonthsLater = new Date(today);
            threeMonthsLater.setMonth(threeMonthsLater.getMonth() + 3);
            
            document.getElementById('start-date').value = today.toISOString().split('T')[0];
            document.getElementById('end-date').value = threeMonthsLater.toISOString().split('T')[0];
        });
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
        blocked_slots = BlockedSlot.query.order_by(BlockedSlot.date.desc(), BlockedSlot.time.desc()).all()
        
        total_bookings = len(bookings)
        pending_bookings = len([b for b in bookings if b.status == 'pending'])
        confirmed_bookings = len([b for b in bookings if b.status == 'confirmed'])
        blocked_slots_count = len(blocked_slots)
        
        return render_template_string(ADMIN_TEMPLATE, 
                                    bookings=bookings,
                                    blocked_slots=blocked_slots,
                                    total_bookings=total_bookings,
                                    pending_bookings=pending_bookings,
                                    confirmed_bookings=confirmed_bookings,
                                    blocked_slots_count=blocked_slots_count)
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


@admin_bp.route('/admin/bulk-block', methods=['POST'])
@cross_origin()
def bulk_block_slots():
    """Bulk block time slots"""
    try:
        data = request.get_json()
        
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        selected_days = data['days']  # List of weekday numbers (0=Sunday, 6=Saturday)
        selected_times = data['times']  # List of time strings like "22:00"
        reason = data['reason']
        
        blocked_count = 0
        current_date = start_date
        
        while current_date <= end_date:
            # Check if this date's weekday is in the selected days
            if current_date.weekday() == 6:  # Python weekday: Monday=0, Sunday=6
                weekday_num = 0  # Convert to our format: Sunday=0
            else:
                weekday_num = current_date.weekday() + 1  # Monday=1, Saturday=6
            
            if weekday_num in selected_days:
                # Block all selected times for this date
                for time_str in selected_times:
                    # Check if this slot is already blocked
                    existing_block = BlockedSlot.query.filter_by(
                        date=current_date,
                        time=time_str
                    ).first()
                    
                    if not existing_block:
                        # Create new blocked slot
                        blocked_slot = BlockedSlot(
                            date=current_date,
                            time=time_str,
                            reason=reason
                        )
                        db.session.add(blocked_slot)
                        blocked_count += 1
            
            # Move to next day
            current_date = current_date.replace(day=current_date.day + 1) if current_date.day < 28 else \
                          current_date.replace(month=current_date.month + 1, day=1) if current_date.month < 12 else \
                          current_date.replace(year=current_date.year + 1, month=1, day=1)
            
            # Safety check to prevent infinite loop
            if current_date.year > end_date.year + 1:
                break
        
        db.session.commit()
        return jsonify({'message': f'Successfully blocked {blocked_count} time slots', 'blocked_count': blocked_count})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/blocked-slots/<int:slot_id>', methods=['DELETE'])
@cross_origin()
def delete_blocked_slot(slot_id):
    """Delete a blocked slot"""
    try:
        blocked_slot = BlockedSlot.query.get_or_404(slot_id)
        db.session.delete(blocked_slot)
        db.session.commit()
        
        return jsonify({'message': 'Blocked slot removed successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



@admin_bp.route('/api/blocked-slots', methods=['GET'])
@cross_origin()
def get_blocked_slots():
    """Get all blocked slots for frontend calendar"""
    try:
        blocked_slots = BlockedSlot.query.all()
        blocked_data = {}
        
        for slot in blocked_slots:
            date_str = slot.date.strftime('%Y-%m-%d')
            time_str = slot.time.strftime('%I:%M %p').lstrip('0')
            
            if date_str not in blocked_data:
                blocked_data[date_str] = []
            blocked_data[date_str].append(time_str)
        
        return jsonify(blocked_data)
    except Exception as e:
        print(f"Error fetching blocked slots: {e}")
        return jsonify({}), 500



# API endpoints for static admin interface
@admin_bp.route('/api/bookings', methods=['GET'])
@cross_origin()
def get_all_bookings():
    """Get all bookings for admin dashboard"""
    try:
        bookings = Booking.query.order_by(Booking.created_at.desc()).all()
        bookings_data = []
        
        for booking in bookings:
            bookings_data.append({
                'id': booking.id,
                'name': booking.name,
                'email': booking.email,
                'phone': booking.phone,
                'booking_date': booking.booking_date.strftime('%Y-%m-%d') if booking.booking_date else '',
                'booking_time': booking.booking_time.strftime('%H:%M') if booking.booking_time else '',
                'service_type': booking.service_type,
                'duration': booking.duration,
                'status': booking.status,
                'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M:%S') if booking.created_at else ''
            })
        
        return jsonify(bookings_data)
        
    except Exception as e:
        print(f"Error getting bookings: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/blocked-slots', methods=['GET'])
@cross_origin()
def get_all_blocked_slots():
    """Get all blocked slots for admin dashboard"""
    try:
        blocked_slots = BlockedSlot.query.order_by(BlockedSlot.date, BlockedSlot.time).all()
        slots_data = []
        
        for slot in blocked_slots:
            slots_data.append({
                'id': slot.id,
                'date': slot.date.strftime('%Y-%m-%d') if slot.date else '',
                'time': slot.time.strftime('%H:%M') if slot.time else '',
                'created_at': slot.created_at.strftime('%Y-%m-%d %H:%M:%S') if slot.created_at else ''
            })
        
        return jsonify(slots_data)
        
    except Exception as e:
        print(f"Error getting blocked slots: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/booking/<int:booking_id>', methods=['PUT'])
@cross_origin()
def update_booking_status(booking_id):
    """Update booking status (confirm/cancel)"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['confirmed', 'cancelled', 'pending']:
            return jsonify({'success': False, 'error': 'Invalid status'}), 400
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        booking.status = new_status
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Booking {new_status} successfully'})
        
    except Exception as e:
        print(f"Error updating booking: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/admin/blocked-slot/<int:slot_id>', methods=['DELETE'])
@cross_origin()
def delete_blocked_slot(slot_id):
    """Delete a blocked slot"""
    try:
        slot = BlockedSlot.query.get(slot_id)
        if not slot:
            return jsonify({'success': False, 'error': 'Blocked slot not found'}), 404
        
        db.session.delete(slot)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Blocked slot removed successfully'})
        
    except Exception as e:
        print(f"Error deleting blocked slot: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

