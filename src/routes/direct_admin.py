from flask import Blueprint, render_template_string, request, jsonify, session
from src.models.booking import BlockedSlot, db
from datetime import datetime
import json

direct_admin_bp = Blueprint('direct_admin', __name__)

# Simple HTML template with embedded CSS and JavaScript
ADMIN_TEMPLATE = """
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
        .login-form {
            background: #2a2a2a;
            padding: 30px;
            border-radius: 10px;
            max-width: 400px;
            margin: 100px auto;
        }
        .admin-content {
            background: #2a2a2a;
            padding: 30px;
            border-radius: 10px;
        }
        .input-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #00bcd4;
        }
        input[type="password"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #444;
            border-radius: 5px;
            background: #1a1a1a;
            color: white;
        }
        .btn {
            background: #00bcd4;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }
        .btn:hover { background: #0097a7; }
        .btn-danger { background: #f44336; }
        .btn-danger:hover { background: #d32f2f; }
        .blocked-slots {
            display: grid;
            gap: 20px;
            margin-top: 20px;
        }
        .date-group {
            background: #333;
            padding: 15px;
            border-radius: 8px;
        }
        .date-header {
            color: #00bcd4;
            font-size: 18px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .time-slots {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .time-slot {
            background: #444;
            padding: 8px 12px;
            border-radius: 5px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .delete-btn {
            background: #f44336;
            color: white;
            border: none;
            border-radius: 3px;
            width: 20px;
            height: 20px;
            cursor: pointer;
            font-size: 12px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: #333;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            color: #00bcd4;
            font-weight: bold;
        }
        .message {
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            background: #4caf50;
            color: white;
        }
        .error {
            background: #f44336;
        }
    </style>
</head>
<body>
    <div class="container">
        {% if not authenticated %}
        <div class="login-form">
            <div class="header">
                <h1>🎵 Wave House Admin</h1>
                <p>Manage Blocked Slots</p>
            </div>
            <form method="POST">
                <div class="input-group">
                    <label for="password">Admin Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn">Login</button>
            </form>
            {% if error %}
            <div class="message error">{{ error }}</div>
            {% endif %}
        </div>
        {% else %}
        <div class="header">
            <h1>🎵 Wave House Admin Dashboard</h1>
            <p>Manage Blocked Time Slots</p>
        </div>

        {% if message %}
        <div class="message">{{ message }}</div>
        {% endif %}

        <div class="admin-content">
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{{ stats.total_blocked }}</div>
                    <div>Total Blocked Slots</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ stats.unique_dates }}</div>
                    <div>Blocked Dates</div>
                </div>
            </div>

            <h2>Blocked Time Slots</h2>
            <p style="margin-bottom: 20px; color: #ccc;">
                Click the × button to delete individual time slots, or "Delete All" to remove all slots for a specific date.
            </p>

            <div class="blocked-slots">
                {% for date, slots in blocked_slots.items() %}
                <div class="date-group">
                    <div class="date-header">
                        <span>{{ date }}</span>
                        <button class="btn btn-danger" onclick="deleteAllForDate('{{ date }}')">
                            Delete All for This Date
                        </button>
                    </div>
                    <div class="time-slots">
                        {% for slot in slots %}
                        <div class="time-slot">
                            <span>{{ slot.time }}</span>
                            <button class="delete-btn" onclick="deleteSlot({{ slot.id }})" title="Delete this time slot">×</button>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endfor %}
            </div>

            {% if not blocked_slots %}
            <div style="text-align: center; padding: 40px; color: #666;">
                <h3>No blocked slots found</h3>
                <p>All time slots are currently available for booking.</p>
            </div>
            {% endif %}
        </div>

        <div style="text-align: center; margin-top: 30px;">
            <a href="/admin-access?logout=1" class="btn">Logout</a>
        </div>
        {% endif %}
    </div>

    <script>
        function deleteSlot(slotId) {
            if (confirm('Delete this time slot?')) {
                fetch('/admin-access/delete-slot', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({slot_id: slotId})
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('Error: ' + data.error);
                    }
                });
            }
        }

        function deleteAllForDate(date) {
            if (confirm('Delete ALL time slots for ' + date + '?')) {
                fetch('/admin-access/delete-date', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({date: date})
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('Error: ' + data.error);
                    }
                });
            }
        }
    </script>
</body>
</html>
"""

@direct_admin_bp.route('/admin-access', methods=['GET', 'POST'])
def admin_access():
    # Handle logout
    if request.args.get('logout'):
        session.pop('admin_authenticated', None)
        return render_template_string(ADMIN_TEMPLATE, authenticated=False)
    
    # Check if already authenticated
    if session.get('admin_authenticated'):
        # Get blocked slots data
        blocked_slots = {}
        stats = {'total_blocked': 0, 'unique_dates': 0}
        
        try:
            slots = BlockedSlot.query.all()
            stats['total_blocked'] = len(slots)
            
            for slot in slots:
                date_str = slot.date.strftime('%Y-%m-%d') if slot.date else 'Unknown'
                if date_str not in blocked_slots:
                    blocked_slots[date_str] = []
                blocked_slots[date_str].append(slot)
            
            stats['unique_dates'] = len(blocked_slots)
            
            # Sort dates
            blocked_slots = dict(sorted(blocked_slots.items()))
            
        except Exception as e:
            print(f"Error fetching blocked slots: {e}")
        
        return render_template_string(ADMIN_TEMPLATE, 
                                    authenticated=True, 
                                    blocked_slots=blocked_slots,
                                    stats=stats)
    
    # Handle login
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'admin123':  # Simple password check
            session['admin_authenticated'] = True
            return render_template_string(ADMIN_TEMPLATE, authenticated=True, blocked_slots={}, stats={'total_blocked': 0, 'unique_dates': 0})
        else:
            return render_template_string(ADMIN_TEMPLATE, authenticated=False, error="Invalid password")
    
    return render_template_string(ADMIN_TEMPLATE, authenticated=False)

@direct_admin_bp.route('/admin-access/delete-slot', methods=['POST'])
def delete_slot():
    if not session.get('admin_authenticated'):
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
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
        return jsonify({'success': False, 'error': str(e)})

@direct_admin_bp.route('/admin-access/delete-date', methods=['POST'])
def delete_date():
    if not session.get('admin_authenticated'):
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    try:
        data = request.get_json()
        date_str = data.get('date')
        
        # Parse date
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Delete all slots for this date
        slots = BlockedSlot.query.filter_by(date=date_obj).all()
        for slot in slots:
            db.session.delete(slot)
        
        db.session.commit()
        return jsonify({'success': True, 'deleted_count': len(slots)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

