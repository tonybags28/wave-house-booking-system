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
    """Simple admin interface"""
    admin_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wave House Admin</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Arial, sans-serif; 
            background: #1a1a1a; 
            color: white; 
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { 
            background: linear-gradient(135deg, #00bcd4, #0097a7);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        .admin-content {
            background: #2a2a2a;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
        }
        .btn {
            background: #00bcd4;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin: 10px;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
        }
        .btn:hover { background: #0097a7; }
        .info {
            background: #333;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 Wave House Admin</h1>
            <p>Admin Dashboard</p>
        </div>
        
        <div class="admin-content">
            <h2>Admin Access Confirmed!</h2>
            <p style="margin: 20px 0;">The admin interface is working. Use the Python tool for full blocked slots management.</p>
            
            <div class="info">
                <h3>Blocked Slots Management</h3>
                <p>To manage your blocked time slots, use the Python tool provided:</p>
                <code style="background: #1a1a1a; padding: 10px; display: block; margin: 10px 0; border-radius: 5px;">
                    python3 blocked_slots_manager.py
                </code>
                <p>This tool provides full functionality to:</p>
                <ul style="text-align: left; margin: 10px 0; padding-left: 20px;">
                    <li>View all 1079 blocked slots</li>
                    <li>Delete individual time slots</li>
                    <li>Delete all slots for specific dates</li>
                    <li>Delete date ranges (perfect for when your client leaves town)</li>
                </ul>
            </div>
            
            <a href="/" class="btn">Back to Main Site</a>
        </div>
    </div>
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
    app.run(host='0.0.0.0', port=5000, debug=True)
