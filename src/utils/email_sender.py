import smtplib
import json
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.request
import urllib.parse

def send_booking_notification(booking_data, request_type):
    """Send email notification using Gmail SMTP"""
    try:
        # Gmail SMTP Configuration - Use environment variables for production
        GMAIL_SMTP_SERVER = "smtp.gmail.com"
        GMAIL_SMTP_PORT = 587
        GMAIL_EMAIL = os.getenv("GMAIL_EMAIL", "letswork@wavehousela.com")
        GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "rkyu btcu xqfn rbsx")  # Updated app password
        
        # Format the email content based on request type
        if request_type == "studio-access":
            subject = f"🎵 New Studio Booking Request - {booking_data['name']}"
            message_body = f"""
🎵 NEW STUDIO BOOKING REQUEST

👤 Customer Details:
Name: {booking_data['name']}
Email: {booking_data['email']}
Phone: {booking_data.get('phone', 'Not provided')}

📅 Booking Details:
Date: {booking_data['date']}
Time: {booking_data['time']}
Duration: {booking_data.get('duration', 'Not specified')} hours
Project Type: {booking_data.get('project_type', 'Not specified')}

💬 Message:
{booking_data.get('message', 'No additional message')}

⏰ Submitted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔗 Manage this booking in your admin dashboard.
"""
        elif request_type == "engineer-request":
            subject = f"🎛️ New Engineer Request - {booking_data['name']}"
            message_body = f"""
🎛️ NEW ENGINEER REQUEST

👤 Customer Details:
Name: {booking_data['name']}
Email: {booking_data['email']}
Phone: {booking_data.get('phone', 'Not provided')}

💬 Session Details:
{booking_data.get('message', 'No details provided')}

⏰ Submitted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📧 Reply directly to this customer to discuss engineer availability and pricing.
"""
        else:  # mixing
            subject = f"🎚️ New Mixing Request - {booking_data['name']}"
            message_body = f"""
🎚️ NEW MIXING SERVICES REQUEST

👤 Customer Details:
Name: {booking_data['name']}
Email: {booking_data['email']}
Phone: {booking_data.get('phone', 'Not provided')}

💬 Project Details:
{booking_data.get('message', 'No project details provided')}

⏰ Submitted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📧 Reply directly to this customer to discuss mixing services and pricing.
"""
        
        # Method 1: Gmail SMTP (Primary method)
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = GMAIL_EMAIL
            msg['To'] = GMAIL_EMAIL
            msg['Subject'] = subject
            msg['Reply-To'] = booking_data.get('email', GMAIL_EMAIL)
            
            # Add body to email
            msg.attach(MIMEText(message_body, 'plain'))
            
            # Create SMTP session
            server = smtplib.SMTP(GMAIL_SMTP_SERVER, GMAIL_SMTP_PORT)
            server.starttls()  # Enable security
            server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
            
            # Send email
            text = msg.as_string()
            server.sendmail(GMAIL_EMAIL, GMAIL_EMAIL, text)
            server.quit()
            
            print(f"✅ EMAIL SENT SUCCESSFULLY via Gmail SMTP to {GMAIL_EMAIL}")
            print(f"📧 Subject: {subject}")
            print(f"👤 From: {booking_data['name']} ({booking_data.get('email', 'No email')})")
            print(f"📅 Request Type: {request_type}")
            return True
            
        except Exception as gmail_error:
            print(f"❌ Gmail SMTP failed: {gmail_error}")
            
            # Fallback Method 2: Use Formsubmit.co as backup
            try:
                formsubmit_data = {
                    "_to": "letswork@wavehousela.com",
                    "_subject": subject,
                    "_template": "table",
                    "_captcha": "false",
                    "_autoresponse": "Thank you for contacting Wave House! We'll get back to you within 24 hours.",
                    "name": booking_data['name'],
                    "email": booking_data.get('email', 'noreply@wavehousela.com'),
                    "phone": booking_data.get('phone', 'Not provided'),
                    "message": message_body,
                    "request_type": request_type,
                    "date": booking_data.get('date', ''),
                    "time": booking_data.get('time', ''),
                    "duration": booking_data.get('duration', ''),
                    "project_type": booking_data.get('project_type', '')
                }
                
                data = urllib.parse.urlencode(formsubmit_data).encode('utf-8')
                req = urllib.request.Request(
                    "https://formsubmit.co/letswork@wavehousela.com",
                    data=data,
                    headers={
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Accept': 'application/json'
                    }
                )
                
                with urllib.request.urlopen(req, timeout=15) as response:
                    response_data = response.read().decode('utf-8')
                    if response.getcode() in [200, 201]:
                        print(f"✅ EMAIL SENT SUCCESSFULLY via FormSubmit (backup) to letswork@wavehousela.com")
                        print(f"Subject: {subject}")
                        return True
                        
            except Exception as formsubmit_error:
                print(f"❌ FormSubmit backup failed: {formsubmit_error}")
        
        # Enhanced logging with clear email content
        print("=" * 60)
        print("📧 EMAIL NOTIFICATION (Logging - All Methods Failed)")
        print("=" * 60)
        print(f"📬 TO: letswork@wavehousela.com")
        print(f"📝 FROM: {booking_data.get('email', 'noreply@wavehousela.com')}")
        print(f"👤 NAME: {booking_data['name']}")
        print(f"📋 SUBJECT: {subject}")
        print("=" * 60)
        print("💬 MESSAGE:")
        print(message_body)
        print("=" * 60)
        print("⚠️  EMAIL METHODS ATTEMPTED:")
        print("1. Gmail SMTP (Primary)")
        print("2. FormSubmit.co (Backup)")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Email system error: {str(e)}")
        return False

