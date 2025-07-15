import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.booking import Booking, BlockedSlot
from src.models.client import Client
from src.routes.user import user_bp
from src.routes.booking import booking_bp
from src.routes.admin import admin_bp
from src.routes.payment import payment_bp
from src.routes.verification import verification_bp
from src.routes.simple_booking import simple_booking_bp
from src.routes.direct_admin import direct_admin_bp

# Import database initialization
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def initialize_database():
    """Initialize database tables for Wave House booking system"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("No DATABASE_URL found, skipping database initialization")
        return
    
    try:
        print("🚀 Initializing Wave House database tables...")
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create bookings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                phone VARCHAR(50),
                project_type VARCHAR(100),
                booking_date DATE NOT NULL,
                booking_time TIME NOT NULL,
                duration INTEGER DEFAULT 4,
                service_type VARCHAR(50) NOT NULL,
                additional_info TEXT,
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create contact_messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_messages (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                status VARCHAR(50) DEFAULT 'unread',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.close()
        conn.close()
        print("✅ Wave House database tables initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes with comprehensive settings
CORS(app, origins=['*'], methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'], 
     allow_headers=['Content-Type', 'Authorization'], supports_credentials=True)

# Register blueprints BEFORE catch-all route to ensure proper routing
app.register_blueprint(direct_admin_bp)  # Register direct admin first for immediate access
app.register_blueprint(admin_bp)  # Register admin first to avoid conflicts
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(booking_bp, url_prefix='/api')
app.register_blueprint(simple_booking_bp, url_prefix='/api')
app.register_blueprint(payment_bp)
app.register_blueprint(verification_bp)

# Database configuration for Railway
database_url = os.getenv('DATABASE_URL')
if database_url:
    # Railway PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Fallback to SQLite for local development
    database_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'database', 'app.db'))
    os.makedirs(os.path.dirname(database_path), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")  # Debug logging
db.init_app(app)
with app.app_context():
    db.create_all()
    print("Database tables created successfully")  # Debug logging
    
    # Initialize Wave House specific tables
    initialize_database()

@app.route('/admin')
def admin():
    """Comprehensive admin dashboard"""
    from src.models.booking import Booking, BlockedSlot
    from src.models.client import Client
    from datetime import datetime
    
    try:
        # Get all bookings
        bookings = Booking.query.order_by(Booking.created_at.desc()).all()
        
        # Get all blocked slots
        blocked_slots = BlockedSlot.query.order_by(BlockedSlot.date, BlockedSlot.time).all()
        
        # Get stats
        total_bookings = len(bookings)
        pending_bookings = len([b for b in bookings if b.status == 'pending'])
        confirmed_bookings = len([b for b in bookings if b.status == 'confirmed'])
        total_blocked = len(blocked_slots)
        
    except Exception as e:
        print(f"Database error: {e}")
        bookings = []
        blocked_slots = []
        total_bookings = pending_bookings = confirmed_bookings = total_blocked = 0
    
    admin_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wave House Admin Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: Arial, sans-serif; 
            background: #1a1a1a; 
            color: white; 
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ 
            background: linear-gradient(135deg, #00bcd4, #0097a7);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: #2a2a2a;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 2.5em;
            color: #00bcd4;
            font-weight: bold;
        }}
        .section {{
            background: #2a2a2a;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .section h2 {{
            color: #00bcd4;
            margin-bottom: 15px;
            border-bottom: 2px solid #00bcd4;
            padding-bottom: 10px;
        }}
        .booking-item {{
            background: #333;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            display: grid;
            grid-template-columns: 1fr 1fr 1fr auto;
            gap: 15px;
            align-items: center;
        }}
        .booking-pending {{ border-left: 4px solid #ff9800; }}
        .booking-confirmed {{ border-left: 4px solid #4caf50; }}
        .booking-cancelled {{ border-left: 4px solid #f44336; }}
        .btn {{
            background: #00bcd4;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            font-size: 14px;
            margin: 2px;
        }}
        .btn:hover {{ background: #0097a7; }}
        .btn-success {{ background: #4caf50; }}
        .btn-success:hover {{ background: #45a049; }}
        .btn-danger {{ background: #f44336; }}
        .btn-danger:hover {{ background: #d32f2f; }}
        .blocked-slot {{
            background: #444;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .status-pending {{ color: #ff9800; }}
        .status-confirmed {{ color: #4caf50; }}
        .status-cancelled {{ color: #f44336; }}
        .no-data {{
            text-align: center;
            color: #666;
            padding: 40px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 Wave House Admin Dashboard</h1>
            <p>Complete Booking Management System</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{total_bookings}</div>
                <div>Total Bookings</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{pending_bookings}</div>
                <div>Pending Bookings</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{confirmed_bookings}</div>
                <div>Confirmed Bookings</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_blocked}</div>
                <div>Blocked Slots</div>
            </div>
        </div>

        <div class="section">
            <h2>📅 Recent Bookings</h2>
            {"".join([f'''
            <div class="booking-item booking-{booking.status}">
                <div>
                    <strong>{booking.name}</strong><br>
                    <small>{booking.email}</small>
                </div>
                <div>
                    {booking.booking_date} at {booking.booking_time}<br>
                    <small>{booking.service_type} - {booking.duration}hrs</small>
                </div>
                <div>
                    <span class="status-{booking.status}">●</span> {booking.status.title()}
                </div>
                <div>
                    <button class="btn btn-success" onclick="updateBooking({booking.id}, 'confirmed')">Confirm</button>
                    <button class="btn btn-danger" onclick="updateBooking({booking.id}, 'cancelled')">Cancel</button>
                </div>
            </div>
            ''' for booking in bookings[:10]]) if bookings else '<div class="no-data">No bookings found</div>'}
        </div>

        <div class="section">
            <h2>🚫 Blocked Time Slots</h2>
            <p style="margin-bottom: 15px;">Manage blocked time slots for your monthly client</p>
            {"".join([f'''
            <div class="blocked-slot">
                <span>{slot.date} at {slot.time}</span>
                <button class="btn btn-danger" onclick="deleteBlockedSlot({slot.id})">Remove</button>
            </div>
            ''' for slot in blocked_slots[:20]]) if blocked_slots else '<div class="no-data">No blocked slots found</div>'}
            {f'<p style="margin-top: 15px; color: #666;">Showing 20 of {total_blocked} blocked slots</p>' if total_blocked > 20 else ''}
        </div>

        <div style="text-align: center; margin-top: 30px;">
            <a href="/" class="btn">Back to Main Site</a>
            <a href="/admin-access" class="btn">Advanced Admin</a>
        </div>
    </div>

    <script>
        function updateBooking(bookingId, status) {{
            if (confirm(`Are you sure you want to ${{status}} this booking?`)) {{
                fetch('/api/admin/booking/' + bookingId, {{
                    method: 'PUT',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{status: status}})
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        location.reload();
                    }} else {{
                        alert('Error: ' + data.error);
                    }}
                }});
            }}
        }}

        function deleteBlockedSlot(slotId) {{
            if (confirm('Remove this blocked time slot?')) {{
                fetch('/api/admin/blocked-slot/' + slotId, {{
                    method: 'DELETE',
                    headers: {{'Content-Type': 'application/json'}}
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        location.reload();
                    }} else {{
                        alert('Error: ' + data.error);
                    }}
                }});
            }}
        }}
    </script>
</body>
</html>
    """
    return admin_html

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    # Use PORT provided by Railway or default to 5000 for local development
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
