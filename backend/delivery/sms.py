import os
from twilio.rest import Client

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM_NUMBER")


def send_sms(farmer_id, advisory):
    # Lookup farmer phone number (stub)
    phone_number = get_farmer_phone(farmer_id)
    if not phone_number:
        print(f"No phone number for farmer {farmer_id}")
        return
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    message = client.messages.create(
        body=advisory,
        from_=TWILIO_FROM,
        to=phone_number,
    )
    print(f"SMS sent to {farmer_id} ({phone_number}): {advisory}")


def get_farmer_phone(farmer_id):
    # Replace with actual lookup (stub)
    return os.getenv("TEST_FARMER_PHONE", "+911234567890")