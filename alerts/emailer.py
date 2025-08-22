"""Alert system for SLA violations."""

import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from datetime import datetime

from config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    WEBHOOK_URL,
    WEBHOOK_SECRET,
    SMS_PROVIDER_API_KEY,
    SMS_SENDER_ID
)

def send_email_alert(
    recipients: List[str],
    subject: str,
    violations: Dict[str, any],
    vendor_name: str
) -> bool:
    """
    Send email alert for SLA violations.
    
    Args:
        recipients: List of email addresses
        subject: Email subject
        violations: Dictionary of violations
        vendor_name: Name of the vendor
    
    Returns:
        bool: True if email sent successfully
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = f"SLA Alert: {subject}"
        
        # Create HTML content
        html = f"""
        <html>
            <body>
                <h2>SLA Violation Alert</h2>
                <p><strong>Vendor:</strong> {vendor_name}</p>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <h3>Violations:</h3>
                <ul>
        """
        
        for category, details in violations.items():
            html += f"<li><strong>{category}:</strong> {details}</li>"
        
        html += """
                </ul>
                <p>Please take necessary action.</p>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        # Connect to SMTP server
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def send_sms_alert(
    phone_numbers: List[str],
    message: str
) -> bool:
    """
    Send SMS alert (stub for future implementation).
    
    Args:
        phone_numbers: List of phone numbers
        message: SMS message
    
    Returns:
        bool: True if SMS sent successfully
    """
    try:
        # TODO: Implement SMS provider integration
        print(f"SMS Alert (TODO): {message} to {phone_numbers}")
        return True
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        return False

def send_webhook_alert(
    data: Dict[str, any],
    endpoint: Optional[str] = None
) -> bool:
    """
    Send webhook alert (stub for future implementation).
    
    Args:
        data: Alert data to send
        endpoint: Optional custom webhook endpoint
    
    Returns:
        bool: True if webhook sent successfully
    """
    try:
        url = endpoint or WEBHOOK_URL
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Secret": WEBHOOK_SECRET
        }
        
        response = requests.post(url, json=data, headers=headers)
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error sending webhook: {str(e)}")
        return False

def send_alert(
    alert_type: str,
    recipients: List[str],
    subject: str,
    data: Dict[str, any],
    vendor_name: str
) -> bool:
    """
    Send alert based on type.
    
    Args:
        alert_type: Type of alert ("email", "sms", or "webhook")
        recipients: List of recipients
        subject: Alert subject
        data: Alert data
        vendor_name: Name of the vendor
    
    Returns:
        bool: True if alert sent successfully
    """
    if alert_type == "email":
        return send_email_alert(recipients, subject, data, vendor_name)
    elif alert_type == "sms":
        message = f"SLA Alert: {subject} - Vendor: {vendor_name}"
        return send_sms_alert(recipients, message)
    elif alert_type == "webhook":
        webhook_data = {
            "type": "sla_violation",
            "subject": subject,
            "vendor": vendor_name,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        return send_webhook_alert(webhook_data)
    else:
        print(f"Unsupported alert type: {alert_type}")
        return False 