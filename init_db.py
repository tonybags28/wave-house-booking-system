#!/usr/bin/env python3
"""
Database initialization script for Wave House booking system
Creates all necessary tables for the booking system to function
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database_tables():
    """Create all necessary tables for the Wave House booking system"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not found")
        return False
    
    try:
        # Connect to database
        print("Connecting to database...")
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create bookings table
        print("Creating bookings table...")
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
        
        # Create engineer_requests table
        print("Creating engineer_requests table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS engineer_requests (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                phone VARCHAR(50),
                project_type VARCHAR(100),
                experience_level VARCHAR(50),
                budget_range VARCHAR(50),
                preferred_date DATE,
                additional_info TEXT,
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create mixing_requests table
        print("Creating mixing_requests table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mixing_requests (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                phone VARCHAR(50),
                project_name VARCHAR(255),
                track_count INTEGER,
                genre VARCHAR(100),
                deadline DATE,
                budget_range VARCHAR(50),
                file_format VARCHAR(50),
                additional_info TEXT,
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create contact_messages table
        print("Creating contact_messages table...")
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
        
        print("✅ All tables created successfully!")
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Initializing Wave House database...")
    success = create_database_tables()
    if success:
        print("🎉 Database initialization completed successfully!")
    else:
        print("💥 Database initialization failed!")

