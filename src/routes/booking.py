from flask import Blueprint, request, jsonify
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

