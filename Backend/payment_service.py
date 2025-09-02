"""
MAZINGIRA MIND - PAYMENT SERVICE MODULE
InstaSend integration for handling payments in Kenya
"""
import os
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class InstaSendPayment:
    """
    INSTASEND PAYMENT INTEGRATION
    Handles M-Pesa and card payments for Kenyan users
    """

    def __init__(self):
        self.api_key = os.environ.get('INSTASEND_API_KEY')
        self.api_secret = os.environ.get('INSTASEND_API_SECRET')
        self.base_url = os.environ.get('INSTASEND_BASE_URL', 'https://payment.intasend.com/api/v1/')
        self.frontend_base = os.environ.get('FRONTEND_BASE_URL', '').rstrip("/")
        self.backend_base = os.environ.get('BACKEND_BASE_URL', '').rstrip("/")

        if not self.api_key or not self.api_secret:
            logger.warning("InstaSend credentials not configured")
            self.configured = False
        else:
            self.configured = True
            logger.info("✅ InstaSend payment service initialized")

    # ---------- Helpers ----------
    def _success_url(self):
        # If serving frontend via Flask on same port, this route exists
        if self.frontend_base:
            return f"{self.frontend_base}/payment-success"
        # fallback to same-origin
        return "/payment-success"

    def _webhook_url(self):
        # Publicly reachable URL recommended (ngrok/Render/etc.)
        if self.backend_base:
            return f"{self.backend_base}/api/pay/webhook"
        # fallback to local dev
        return "http://localhost:5000/api/pay/webhook"

    def format_kenyan_phone(self, phone_number: str):
        digits = "".join([c for c in str(phone_number) if c.isdigit()])
        if digits.startswith("254"):
            return f"+{digits}"
        if digits.startswith("0"):
            return f"+254{digits[1:]}"
        if len(digits) == 9:
            return f"+254{digits}"
        return phone_number

    def generate_api_reference(self, payment_data):
        ts = int(datetime.now().timestamp())
        return f"mazingira_{payment_data['service_type']}_{payment_data['user_id']}_{ts}"

    # ---------- API ----------
    def create_payment_request(self, payment_data: dict):
        try:
            if not self.configured:
                return {'success': False, 'error': 'Payment service not configured'}

            request_data = {
                'amount': payment_data['amount'],
                'currency': 'KES',
                'email': payment_data.get('email', ''),
                'phone_number': self.format_kenyan_phone(payment_data['phone_number']),
                'api_ref': self.generate_api_reference(payment_data),
                'method': ['MPESA-STK-PUSH', 'CARD-PAYMENT'],
                'redirect_url': self._success_url(),
                'webhook_url': self._webhook_url(),
                'extra': {
                    'service_type': payment_data['service_type'],
                    'user_id': payment_data['user_id']
                }
            }

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            resp = requests.post(f'{self.base_url}checkout/', headers=headers, json=request_data, timeout=30)
            if resp.status_code == 201:
                result = resp.json()
                # TODO: Persist a Payment row if you have a model
                logger.info(f"Payment created for {payment_data['user_id']} KES {payment_data['amount']}")
                return {
                    'success': True,
                    'payment_url': result.get('url'),
                    'reference': result.get('invoice', {}).get('invoice_id', ''),
                    'message': 'Payment request created successfully'
                }

            try:
                detail = resp.json().get('detail') or resp.json().get('error') or f'HTTP {resp.status_code}'
            except Exception:
                detail = f'HTTP {resp.status_code}'
            logger.error(f"InstaSend error: {detail}")
            return {'success': False, 'error': f'Payment creation failed: {detail}'}

        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Payment service timeout - please try again'}
        except Exception as e:
            logger.error(f"Unexpected payment error: {e}")
            return {'success': False, 'error': 'Payment service temporarily unavailable'}

    def process_webhook(self, webhook_data: dict):
        try:
            invoice_id = webhook_data.get('invoice_id')
            status = (webhook_data.get('state') or '').upper()
            api_ref = webhook_data.get('api_ref', '')

            logger.info(f"Webhook received: {invoice_id} - {status}")

            if status == 'COMPLETE':
                user_id, service_type = self.parse_api_reference(api_ref)
                # TODO: update DB records / entitlements
                logger.info(f"✅ Payment COMPLETE for user {user_id} - {service_type}")
                return {'success': True, 'message': 'Payment processed', 'user_id': user_id, 'service_type': service_type}

            if status == 'FAILED':
                logger.warning(f"❌ Payment FAILED: {invoice_id}")
                return {'success': True, 'message': 'Payment failed'}

            return {'success': True, 'message': 'Webhook processed'}
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            return {'success': False, 'error': 'Webhook processing failed'}

    def parse_api_reference(self, api_ref: str):
        # mazingira_{service_type}_{user_id}_{timestamp}
        parts = str(api_ref).split("_")
        if len(parts) >= 4 and parts[0] == "mazingira":
            return parts[2], parts[1]
        return None, None
