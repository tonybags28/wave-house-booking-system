from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Import db from user model to use the same instance
from .user import db

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(20), nullable=False)
    duration = db.Column(db.String(10), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    project_type = db.Column(db.String(50), nullable=True)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled
    
    # Client verification fields
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=True)
    requires_verification = db.Column(db.Boolean, default=False, nullable=False)
    verification_completed = db.Column(db.Boolean, default=False, nullable=False)
    verification_session_id = db.Column(db.String(100), nullable=True)
    
    # Payment fields (for future payment integration)
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid, paid, refunded
    payment_amount = db.Column(db.Float, nullable=True)
    stripe_payment_intent_id = db.Column(db.String(100), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'service_type': self.service_type,
            'date': self.date.isoformat() if self.date else None,
            'time': self.time,
            'duration': self.duration,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'project_type': self.project_type,
            'message': self.message,
            'status': self.status,
            'client_id': self.client_id,
            'requires_verification': self.requires_verification,
            'verification_completed': self.verification_completed,
            'verification_session_id': self.verification_session_id,
            'payment_status': self.payment_status,
            'payment_amount': self.payment_amount,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class BlockedSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(20), nullable=False)
    reason = db.Column(db.String(100), nullable=True)  # maintenance, holiday, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'time': self.time,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
