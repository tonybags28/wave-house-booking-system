from flask import Blueprint, request, jsonify, session, redirect, render_template_string
from datetime import datetime, date, timedelta
from src.models.booking import db, Booking, BlockedSlot
from src.utils.email_sender import send_booking_notification
from flask_cors import cross_origin

booking_bp = Blueprint('booking', __name__)

def time_to_minutes(time_str):
    """Convert time string like '2:00 PM' to minutes since midnight"""
    try:
        time_obj = datetime.strptime(time_str, '%I:%M %p').time()
        return time_obj.hour * 60 + time_obj.minute
    except:
        return 0

def minutes_to_time(minutes):
    """Convert minutes since midnight to time string like '2:00 PM'"""
    hours = minutes // 60
    mins = minutes % 60
    
    if hours == 0:
        return f"12:{mins:02d} AM"
    elif hours < 12:
        return f"{hours}:{mins:02d} AM"
    elif hours == 12:
        return f"12:{mins:02d} PM"
    else:
        return f"{hours-12}:{mins:02d} PM"

def get_time_range(start_time, duration_hours):
    """Get all time slots occupied by a booking"""
    start_minutes = time_to_minutes(start_time)
    duration_minutes = int(duration_hours) * 60
    
    occupied_slots = []
    current_minutes = start_minutes
    
    # Generate all hourly slots within the duration
    while current_minutes < start_minutes + duration_minutes:
        occupied_slots.append(minutes_to_time(current_minutes))
        current_minutes += 60
        
        # Handle day overflow (past midnight)
        if current_minutes >= 24 * 60:
            break
    
    return occupied_slots

def check_booking_conflicts(booking_date, start_time, duration):
    """Check if a new booking conflicts with existing bookings"""
    if not duration:
        return False
        
    try:
        duration_int = int(duration)
    except (ValueError, TypeError):
        return False
        
    # Get the time slots this booking would occupy
    new_booking_slots = get_time_range(start_time, duration_int)
    
    # Get all confirmed bookings for this date
    existing_bookings = Booking.query.filter_by(
        date=booking_date,
        status='confirmed'
    ).all()
    
    # Check each existing booking for conflicts
    for booking in existing_bookings:
        if booking.duration and booking.duration != '':
            try:
                existing_duration = int(booking.duration)
                if existing_duration > 0:
                    existing_slots = get_time_range(booking.time, existing_duration)
                    
                    # Check for any overlap
                    for slot in new_booking_slots:
                        if slot in existing_slots:
                            return True
            except (ValueError, TypeError):
                continue
    
    return False

@booking_bp.route('/bookings', methods=['POST'])
@cross_origin()
def create_booking():
    try:
        data = request.get_json()
        
        # Parse the date string
        booking_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        
        # Check for duration-based conflicts
        if data.get('duration'):
            if check_booking_conflicts(booking_date, data['time'], data['duration']):
                return jsonify({'error': 'This time slot conflicts with an existing booking'}), 400
        
        # Check if the exact slot is already booked (for single-hour bookings)
        existing_booking = Booking.query.filter_by(
            date=booking_date,
            time=data['time'],
            status='confirmed'
        ).first()
        
        if existing_booking:
            return jsonify({'error': 'This time slot is already booked'}), 400
        
        # Check if the slot is blocked
        blocked_slot = BlockedSlot.query.filter_by(
            date=booking_date,
            time=data['time']
        ).first()
        
        if blocked_slot:
            return jsonify({'error': 'This time slot is not available'}), 400
        
        # Import Client model here to avoid circular imports
        from src.models.client import Client
        
        # Check if client exists and their verification status
        client = Client.query.filter_by(email=data['email']).first()
        requires_verification = False
        client_id = None
        
        if not client:
            # New client - create profile and require verification
            client = Client(
                email=data['email'],
                name=data['name'],
                phone=data.get('phone'),
                verification_status='pending'
            )
            db.session.add(client)
            db.session.flush()  # Get the ID without committing
            requires_verification = True
            client_id = client.id
        else:
            # Existing client - check if they need verification
            client_id = client.id
            requires_verification = client.needs_verification()
            
            # Update client info if needed
            if client.name != data['name']:
                client.name = data['name']
            if data.get('phone') and client.phone != data.get('phone'):
                client.phone = data.get('phone')
        
        # Create new booking
        booking = Booking(
            service_type=data['service_type'],
            date=booking_date,
            time=data['time'],
            duration=data.get('duration'),
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            project_type=data.get('project_type'),
            message=data.get('message'),
            status='pending',
            client_id=client_id,
            requires_verification=requires_verification,
            verification_completed=not requires_verification
        )
        
        print(f"Creating booking: {data['name']} for {booking_date} at {data['time']}")  # Debug logging
        print(f"Client verification required: {requires_verification}")  # Debug logging
        
        db.session.add(booking)
        db.session.commit()
        print(f"Booking saved with ID: {booking.id}")  # Debug logging
        
        # Update client booking stats if this is a confirmed booking
        if not requires_verification:
            # Calculate booking amount (you can customize this logic)
            booking_amount = 0
            if data.get('duration'):
                duration_hours = int(data.get('duration', 0))
                # Simple pricing logic - you can make this more sophisticated
                if duration_hours == 4:
                    booking_amount = 100
                elif duration_hours == 6:
                    booking_amount = 130
                elif duration_hours == 8:
                    booking_amount = 160
                elif duration_hours == 12:
                    booking_amount = 230
                elif duration_hours == 24:
                    booking_amount = 400
            
            client.update_booking_stats(booking_amount)
            db.session.commit()
        
        # Verify the booking was saved
        saved_booking = Booking.query.get(booking.id)
        if saved_booking:
            print(f"Booking verified in database: {saved_booking.name}")
        else:
            print("ERROR: Booking not found after save!")
        
        # Send email notification
        booking_data = {
            'name': data['name'],
            'email': data['email'],
            'phone': data.get('phone', ''),
            'date': data['date'],
            'time': data['time'],
            'duration': data.get('duration', ''),
            'project_type': data.get('project_type', ''),
            'message': data.get('message', '')
        }
        send_booking_notification(booking_data, "studio-access")
        
        response_data = {
            'message': 'Booking request submitted successfully',
            'booking': booking.to_dict(),
            'requires_verification': requires_verification,
            'client_id': client_id
        }
        
        if requires_verification:
            response_data['verification_message'] = 'ID verification required for first-time clients'
        
        return jsonify(response_data), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating booking: {str(e)}")  # Debug logging
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/bookings', methods=['GET'])
@cross_origin()
def get_bookings():
    try:
        bookings = Booking.query.all()
        return jsonify([booking.to_dict() for booking in bookings])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/bookings/<int:booking_id>', methods=['PUT'])
@cross_origin()
def update_booking_status(booking_id):
    try:
        data = request.get_json()
        booking = Booking.query.get_or_404(booking_id)
        
        if 'status' in data:
            booking.status = data['status']
        
        db.session.commit()
        return jsonify(booking.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/availability', methods=['GET'])
@cross_origin()
def get_availability():
    try:
        # Get all confirmed bookings
        bookings = Booking.query.filter_by(status='confirmed').all()
        print(f"Found {len(bookings)} confirmed bookings")  # Debug logging
        for booking in bookings:
            print(f"  - {booking.name}: {booking.date} at {booking.time} for {booking.duration} hours")
        
        # Get all blocked slots
        blocked_slots = BlockedSlot.query.all()
        print(f"Found {len(blocked_slots)} blocked slots")  # Debug logging
        
        unavailable = {}
        
        # Add manually blocked slots
        for blocked in blocked_slots:
            date_str = blocked.date.isoformat()
            if date_str not in unavailable:
                unavailable[date_str] = []
            unavailable[date_str].append(blocked.time)
        
        # Add booking conflicts based on duration
        for booking in bookings:
            if booking.duration and booking.duration != '':
                try:
                    # Ensure duration is converted to integer
                    duration_int = int(booking.duration)
                    if duration_int > 0:
                        # Get all time slots occupied by this booking
                        occupied_slots = get_time_range(booking.time, duration_int)
                        print(f"Booking {booking.name} occupies slots: {occupied_slots}")  # Debug logging
                        date_str = booking.date.isoformat()
                        
                        if date_str not in unavailable:
                            unavailable[date_str] = []
                        
                        # Add all occupied slots to unavailable
                        for slot in occupied_slots:
                            if slot not in unavailable[date_str]:
                                unavailable[date_str].append(slot)
                except (ValueError, TypeError):
                    # Skip bookings with invalid duration
                    print(f"Skipping booking {booking.name} - invalid duration: {booking.duration}")
                    continue
            else:
                # Single time slot booking
                date_str = booking.date.isoformat()
                if date_str not in unavailable:
                    unavailable[date_str] = []
                if booking.time not in unavailable[date_str]:
                    unavailable[date_str].append(booking.time)
        
        print(f"Final unavailable slots: {unavailable}")  # Debug logging
        return jsonify(unavailable)
        
    except Exception as e:
        print(f"Error in get_availability: {str(e)}")  # Debug logging
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/blocked-slots', methods=['POST'])
@cross_origin()
def create_blocked_slot():
    try:
        data = request.get_json()
        
        # Parse the date string
        block_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        
        blocked_slot = BlockedSlot(
            date=block_date,
            time=data['time'],
            reason=data.get('reason', 'Blocked by admin')
        )
        
        db.session.add(blocked_slot)
        db.session.commit()
        
        return jsonify({
            'message': 'Time slot blocked successfully',
            'blocked_slot': blocked_slot.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/blocked-slots', methods=['GET'])
@cross_origin()
def get_blocked_slots():
    """Get all blocked slots for frontend calendar integration"""
    try:
        # Simple approach - just return the blocked slots in the expected format
        from flask import jsonify
        
        blocked_slots = BlockedSlot.query.all()
        blocked_data = {}
        
        for slot in blocked_slots:
            # Convert date to string
            if hasattr(slot.date, 'strftime'):
                date_str = slot.date.strftime('%Y-%m-%d')
            else:
                date_str = str(slot.date)
            
            # Convert time to 12-hour format
            if hasattr(slot.time, 'strftime'):
                time_str = slot.time.strftime('%I:%M %p').lstrip('0')
            else:
                # Handle time as string
                time_str = str(slot.time)
                if ':' in time_str:
                    hour, minute = time_str.split(':')
                    hour = int(hour)
                    if hour == 0:
                        time_str = f"12:{minute} AM"
                    elif hour < 12:
                        time_str = f"{hour}:{minute} AM"
                    elif hour == 12:
                        time_str = f"12:{minute} PM"
                    else:
                        time_str = f"{hour-12}:{minute} PM"
            
            if date_str not in blocked_data:
                blocked_data[date_str] = []
            blocked_data[date_str].append(time_str)
        
        return jsonify(blocked_data)
        
    except Exception as e:
        # Return empty object on any error to prevent breaking the frontend
        return jsonify({})

@booking_bp.route('/blocked-slots/<int:slot_id>', methods=['DELETE'])
@cross_origin()
def delete_blocked_slot(slot_id):
    try:
        blocked_slot = BlockedSlot.query.get_or_404(slot_id)
        db.session.delete(blocked_slot)
        db.session.commit()
        
        return jsonify({'message': 'Blocked slot removed successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@booking_bp.route('/engineer-request', methods=['POST'])
@cross_origin()
def create_engineer_request():
    try:
        data = request.get_json()
        
        # Create a special booking entry for engineer requests
        engineer_request = Booking(
            service_type='engineer-request',
            date=date.today(),  # Use today's date as placeholder
            time='00:00 AM',    # Use placeholder time
            duration=None,
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            project_type='engineer-request',
            message=data['message'],
            status='engineer-request'
        )
        
        db.session.add(engineer_request)
        db.session.commit()
        
        # Send email notification
        request_data = {
            'name': data['name'],
            'email': data['email'],
            'phone': data.get('phone', ''),
            'message': data['message']
        }
        send_booking_notification(request_data, "engineer-request")
        
        return jsonify({
            'message': 'Engineer request submitted successfully',
            'request': engineer_request.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/mixing-request', methods=['POST'])
@cross_origin()
def create_mixing_request():
    try:
        data = request.get_json()
        
        # Create a special booking entry for mixing requests
        mixing_request = Booking(
            service_type='mixing-request',
            date=date.today(),  # Use today's date as placeholder
            time='00:00 AM',    # Use placeholder time
            duration=None,
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            project_type='mixing-request',
            message=data['message'],
            status='mixing-request'
        )
        
        db.session.add(mixing_request)
        db.session.commit()
        
        # Send email notification
        request_data = {
            'name': data['name'],
            'email': data['email'],
            'phone': data.get('phone', ''),
            'message': data['message']
        }
        send_booking_notification(request_data, "mixing")
        
        return jsonify({
            'message': 'Mixing request submitted successfully',
            'request': mixing_request.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



# ============================================================================
# ADMIN INTERFACE (Temporary workaround for admin blueprint issues)
# ============================================================================

@booking_bp.route('/wave-admin', methods=['GET', 'POST'])
def wave_admin_dashboard():
    """Admin dashboard with authentication"""
    if request.method == 'POST':
        # Handle login
        password = request.form.get('password')
        if password and password.strip() == "admin123":
            # Simple session-based auth
            from flask import session
            session['wave_admin_authenticated'] = True
            return wave_admin_dashboard_view()
        else:
            return render_admin_login(error="Incorrect password")
    
    # Check if already authenticated
    from flask import session
    if session.get('wave_admin_authenticated'):
        return wave_admin_dashboard_view()
    else:
        return render_admin_login()

def render_admin_login(error=None):
    """Render admin login page"""
    error_msg = f'<div style="color: red; margin-bottom: 10px;">{error}</div>' if error else ''
    
    login_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Wave House Admin - Login</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                margin: 0; 
                padding: 0; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                min-height: 100vh;
            }}
            .login-container {{
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 40px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
                text-align: center;
                min-width: 300px;
            }}
            .logo {{
                color: #00d4ff;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            .subtitle {{
                color: #ffffff;
                margin-bottom: 30px;
                opacity: 0.8;
            }}
            input[type="password"] {{
                width: 100%;
                padding: 12px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.1);
                color: white;
                font-size: 16px;
                margin-bottom: 20px;
                box-sizing: border-box;
            }}
            input[type="password"]::placeholder {{
                color: rgba(255, 255, 255, 0.7);
            }}
            button {{
                width: 100%;
                padding: 12px;
                background: #00d4ff;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: background 0.3s;
            }}
            button:hover {{
                background: #00b8e6;
            }}
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="logo">🎵 Wave House</div>
            <div class="subtitle">Admin Dashboard</div>
            {error_msg}
            <form method="post">
                <input type="password" name="password" placeholder="Enter admin password" required>
                <button type="submit">Access Dashboard</button>
            </form>
        </div>
    </body>
    </html>
    """
    return login_html

def wave_admin_dashboard_view():
    """Render the main admin dashboard"""
    # Get statistics
    total_bookings = Booking.query.count()
    pending_bookings = Booking.query.filter_by(status='pending').count()
    confirmed_bookings = Booking.query.filter_by(status='confirmed').count()
    blocked_slots = BlockedSlot.query.count()
    
    dashboard_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Wave House Admin Dashboard</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                min-height: 100vh;
                color: white;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .header h1 {{
                color: #00d4ff;
                font-size: 32px;
                margin: 0;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .stat-number {{
                font-size: 36px;
                font-weight: bold;
                color: #00d4ff;
                margin-bottom: 5px;
            }}
            .stat-label {{
                font-size: 14px;
                opacity: 0.8;
            }}
            .actions {{
                display: flex;
                gap: 15px;
                justify-content: center;
                flex-wrap: wrap;
            }}
            .action-btn {{
                background: #00d4ff;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                transition: background 0.3s;
            }}
            .action-btn:hover {{
                background: #00b8e6;
            }}
            .action-btn.secondary {{
                background: rgba(255, 255, 255, 0.2);
            }}
            .action-btn.secondary:hover {{
                background: rgba(255, 255, 255, 0.3);
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Wave House Admin Dashboard</h1>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{total_bookings}</div>
                <div class="stat-label">Total Bookings</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{pending_bookings}</div>
                <div class="stat-label">Pending</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{confirmed_bookings}</div>
                <div class="stat-label">Confirmed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{blocked_slots}</div>
                <div class="stat-label">Blocked Slots</div>
            </div>
        </div>
        
        <div class="actions">
            <a href="/api/wave-admin/bookings" class="action-btn">Booking Requests</a>
            <a href="/api/wave-admin/bulk-block" class="action-btn">Bulk Block Times</a>
            <a href="/api/wave-admin/manage-blocks" class="action-btn">Manage Blocked Slots</a>
            <a href="/api/wave-admin/logout" class="action-btn secondary">Logout</a>
        </div>
    </body>
    </html>
    """
    return dashboard_html

@booking_bp.route('/wave-admin/logout')
def wave_admin_logout():
    """Logout admin user"""
    from flask import session, redirect
    session.pop('wave_admin_authenticated', None)
    return redirect('/api/wave-admin')

@booking_bp.route('/wave-admin/manage-blocks')
def wave_admin_manage_blocks():
    """Manage blocked slots interface"""
    from flask import session
    if not session.get('wave_admin_authenticated'):
        return redirect('/api/wave-admin')
    
    # Get all blocked slots grouped by date
    blocked_slots = BlockedSlot.query.order_by(BlockedSlot.date, BlockedSlot.time).all()
    
    # Group by date
    slots_by_date = {}
    for slot in blocked_slots:
        date_str = slot.date.strftime('%Y-%m-%d')
        if date_str not in slots_by_date:
            slots_by_date[date_str] = []
        slots_by_date[date_str].append(slot)
    
    # Generate HTML for blocked slots
    slots_html = ""
    for date_str, slots in sorted(slots_by_date.items()):
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        formatted_date = date_obj.strftime('%B %d, %Y')
        
        slots_html += f"""
        <div class="date-group">
            <h3>{formatted_date} ({len(slots)} slots)</h3>
            <div class="date-actions">
                <button onclick="deleteAllForDate('{date_str}')" class="btn-danger">Delete All for This Date</button>
            </div>
            <div class="slots-grid">
        """
        
        for slot in slots:
            time_str = slot.time.strftime('%I:%M %p')
            slots_html += f"""
                <div class="slot-item" data-id="{slot.id}">
                    <span class="slot-time">{time_str}</span>
                    <span class="slot-reason">{slot.reason or 'No reason'}</span>
                    <button onclick="deleteSlot({slot.id})" class="btn-delete">×</button>
                </div>
            """
        
        slots_html += """
            </div>
        </div>
        """
    
    if not slots_html:
        slots_html = "<p>No blocked slots found.</p>"
    
    manage_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Manage Blocked Slots - Wave House Admin</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                min-height: 100vh;
                color: white;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .header h1 {{
                color: #00d4ff;
                font-size: 28px;
                margin: 0;
            }}
            .back-btn {{
                background: rgba(255, 255, 255, 0.2);
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                text-decoration: none;
                display: inline-block;
                margin-bottom: 20px;
            }}
            .date-group {{
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .date-group h3 {{
                color: #00d4ff;
                margin-top: 0;
                margin-bottom: 15px;
            }}
            .date-actions {{
                margin-bottom: 15px;
            }}
            .slots-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 10px;
            }}
            .slot-item {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 10px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .slot-time {{
                font-weight: bold;
                color: #00d4ff;
            }}
            .slot-reason {{
                font-size: 12px;
                opacity: 0.8;
                margin-left: 10px;
                flex-grow: 1;
            }}
            .btn-delete {{
                background: #ff4757;
                color: white;
                border: none;
                border-radius: 4px;
                width: 24px;
                height: 24px;
                cursor: pointer;
                font-size: 16px;
                line-height: 1;
            }}
            .btn-danger {{
                background: #ff4757;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                cursor: pointer;
                font-size: 14px;
            }}
            .btn-danger:hover {{
                background: #ff3742;
            }}
            .success-msg {{
                background: #2ed573;
                color: white;
                padding: 10px;
                border-radius: 6px;
                margin-bottom: 20px;
                display: none;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <a href="/api/wave-admin" class="back-btn">← Back to Dashboard</a>
            <h1>Manage Blocked Slots</h1>
        </div>
        
        <div id="success-msg" class="success-msg"></div>
        
        <div id="blocked-slots">
            {slots_html}
        </div>
        
        <script>
            function deleteSlot(slotId) {{
                if (confirm('Are you sure you want to delete this blocked slot?')) {{
                    fetch('/api/delete-blocked-slot', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{ slot_id: slotId }})
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        if (data.success) {{
                            document.querySelector(`[data-id="${{slotId}}"]`).remove();
                            showSuccess('Blocked slot deleted successfully');
                        }} else {{
                            alert('Error deleting slot: ' + data.error);
                        }}
                    }})
                    .catch(error => {{
                        alert('Error deleting slot: ' + error);
                    }});
                }}
            }}
            
            function deleteAllForDate(dateStr) {{
                if (confirm(`Are you sure you want to delete ALL blocked slots for ${{dateStr}}?`)) {{
                    fetch('/api/delete-blocked-slots-by-date', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{ date: dateStr }})
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        if (data.success) {{
                            location.reload();
                        }} else {{
                            alert('Error deleting slots: ' + data.error);
                        }}
                    }})
                    .catch(error => {{
                        alert('Error deleting slots: ' + error);
                    }});
                }}
            }}
            
            function showSuccess(message) {{
                const successMsg = document.getElementById('success-msg');
                successMsg.textContent = message;
                successMsg.style.display = 'block';
                setTimeout(() => {{
                    successMsg.style.display = 'none';
                }}, 3000);
            }}
        </script>
    </body>
    </html>
    """
    return manage_html

@booking_bp.route('/delete-blocked-slot', methods=['POST'])
def delete_blocked_slot():
    """Delete a single blocked slot"""
    try:
        data = request.get_json()
        slot_id = data.get('slot_id')
        
        slot = BlockedSlot.query.get(slot_id)
        if slot:
            db.session.delete(slot)
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Slot not found'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@booking_bp.route('/delete-blocked-slots-by-date', methods=['POST'])
def delete_blocked_slots_by_date():
    """Delete all blocked slots for a specific date"""
    try:
        data = request.get_json()
        date_str = data.get('date')
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        slots = BlockedSlot.query.filter_by(date=date_obj).all()
        for slot in slots:
            db.session.delete(slot)
        
        db.session.commit()
        return jsonify({'success': True, 'deleted_count': len(slots)})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})



@booking_bp.route('/admin-stats', methods=['GET'])
def get_admin_stats():
    """Get admin dashboard statistics"""
    try:
        total_bookings = Booking.query.count()
        pending_bookings = Booking.query.filter_by(status='pending').count()
        confirmed_bookings = Booking.query.filter_by(status='confirmed').count()
        blocked_slots = BlockedSlot.query.count()
        
        return jsonify({
            'total': total_bookings,
            'pending': pending_bookings,
            'confirmed': confirmed_bookings,
            'blocked': blocked_slots
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@booking_bp.route('/delete-blocked-slot', methods=['POST'])
def delete_blocked_slot():
    """Delete a specific blocked slot"""
    try:
        data = request.get_json()
        slot_id = data.get('slot_id')
        
        if not slot_id:
            return jsonify({'error': 'Slot ID is required'}), 400
        
        slot = BlockedSlot.query.get(slot_id)
        if not slot:
            return jsonify({'error': 'Slot not found'}), 404
        
        db.session.delete(slot)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Blocked slot deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/delete-blocked-slots-by-date', methods=['POST'])
def delete_blocked_slots_by_date():
    """Delete all blocked slots for a specific date"""
    try:
        data = request.get_json()
        date = data.get('date')
        
        if not date:
            return jsonify({'error': 'Date is required'}), 400
        
        # Delete all slots for the specified date
        deleted_count = BlockedSlot.query.filter_by(date=date).delete()
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Deleted {deleted_count} blocked slots for {date}',
            'deleted_count': deleted_count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

