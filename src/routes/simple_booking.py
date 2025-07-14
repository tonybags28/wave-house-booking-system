from flask import Blueprint, request, jsonify
import psycopg2
import os
from datetime import datetime

simple_booking_bp = Blueprint('simple_booking', __name__)

@simple_booking_bp.route('/submit-booking', methods=['POST'])
def submit_booking():
    """Simple booking submission that saves directly to database"""
    try:
        # Get form data
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        print(f"Received booking data: {data}")  # Debug logging
        
        # Get database connection
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("No DATABASE_URL found")
            return jsonify({'error': 'Database not configured'}), 500
        
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Insert booking into database
        cursor.execute("""
            INSERT INTO bookings (
                name, email, phone, project_type, 
                booking_date, booking_time, service_type, 
                additional_info, status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (
            data.get('name', ''),
            data.get('email', ''),
            data.get('phone', ''),
            data.get('project_type', 'Vocal Recording'),
            data.get('date', '2025-07-15'),  # Default date
            data.get('time', '12:00 PM'),    # Default time
            data.get('service_type', 'studio_access'),
            data.get('additional_info', ''),
            'pending'
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Booking saved successfully!")
        return jsonify({'success': True, 'message': 'Booking submitted successfully!'})
        
    except Exception as e:
        print(f"❌ Error saving booking: {e}")
        return jsonify({'error': 'Failed to submit booking'}), 500

