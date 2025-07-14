from datetime import datetime
# Import db from user model to use the same instance
from .user import db

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    
    # ID Verification fields
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_status = db.Column(db.String(20), default='pending', nullable=False)  # pending, verified, failed, manual_review
    stripe_verification_session_id = db.Column(db.String(100), nullable=True)
    verification_date = db.Column(db.DateTime, nullable=True)
    verification_method = db.Column(db.String(50), nullable=True)  # stripe_identity, manual, etc.
    
    # Client profile info
    first_booking_date = db.Column(db.DateTime, nullable=True)
    total_bookings = db.Column(db.Integer, default=0, nullable=False)
    total_spent = db.Column(db.Float, default=0.0, nullable=False)
    
    # Admin notes and flags
    admin_notes = db.Column(db.Text, nullable=True)
    is_flagged = db.Column(db.Boolean, default=False, nullable=False)
    flag_reason = db.Column(db.String(200), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Client {self.name} ({self.email})>'

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'is_verified': self.is_verified,
            'verification_status': self.verification_status,
            'verification_date': self.verification_date.isoformat() if self.verification_date else None,
            'verification_method': self.verification_method,
            'first_booking_date': self.first_booking_date.isoformat() if self.first_booking_date else None,
            'total_bookings': self.total_bookings,
            'total_spent': self.total_spent,
            'admin_notes': self.admin_notes,
            'is_flagged': self.is_flagged,
            'flag_reason': self.flag_reason,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def is_first_time_client(self):
        """Check if this is a first-time client (no previous verified bookings)"""
        return self.total_bookings == 0

    def needs_verification(self):
        """Check if client needs ID verification"""
        return not self.is_verified and self.verification_status in ['pending', 'failed']

    def update_booking_stats(self, booking_amount=0):
        """Update client booking statistics"""
        self.total_bookings += 1
        self.total_spent += booking_amount
        if self.first_booking_date is None:
            self.first_booking_date = datetime.utcnow()
        self.updated_at = datetime.utcnow()

