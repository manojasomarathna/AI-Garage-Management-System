from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
import requests

_logger = logging.getLogger(__name__)


class GarageWhatsApp(models.Model):
    _name = 'garage.whatsapp'
    _description = 'WhatsApp Configuration (Twilio)'

    name = fields.Char(string='Configuration Name', default='WhatsApp Config')
    account_sid = fields.Char(string='Twilio Account SID', required=True)
    auth_token = fields.Char(string='Twilio Auth Token', required=True, password=True)
    from_number = fields.Char(string='From WhatsApp Number', required=True,
                              help='Format: whatsapp:+1415XXXXXXX')
    garage_name = fields.Char(string='Garage Name', required=True)
    garage_phone = fields.Char(string='Garage Phone')
    active = fields.Boolean(default=True)

    def _send_message(self, to_number, body):
        """Send WhatsApp message via Twilio API."""
        if not to_number:
            _logger.warning('WhatsApp: No phone number provided.')
            return False

        # Normalize phone number
        to_number = to_number.replace(' ', '').replace('-', '')
        if not to_number.startswith('+'):
            to_number = '+94' + to_number.lstrip('0')  # Sri Lanka default

        url = f'https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json'
        payload = {
            'From': self.from_number,
            'To': f'whatsapp:{to_number}',
            'Body': body,
        }
        try:
            response = requests.post(url, data=payload,
                                     auth=(self.account_sid, self.auth_token), timeout=10)
            response.raise_for_status()
            _logger.info('WhatsApp sent to %s', to_number)
            return True
        except requests.exceptions.RequestException as e:
            _logger.error('WhatsApp send failed: %s', str(e))
            return False

    def send_service_ready(self, service_order):
        """Notify customer that vehicle is ready for pickup."""
        customer = service_order.customer_id
        vehicle = service_order.vehicle_id
        phone = customer.mobile or customer.phone
        if not phone:
            return
        body = (
            f"Dear {customer.name},\n\n"
            f"Your vehicle *{vehicle.license_plate}* ({vehicle.brand} {vehicle.model}) "
            f"service is complete and ready for pickup.\n\n"
            f"Job Card: {service_order.name}\n"
            f"Total: LKR {service_order.total_amount:,.2f}\n\n"
            f"Thank you for choosing {self.garage_name}!\n"
            f"📞 {self.garage_phone}"
        )
        self._send_message(phone, body)

    def send_service_reminder(self, reminder):
        """Send AI-generated service reminder to customer."""
        customer = reminder.customer_id
        vehicle = reminder.vehicle_id
        phone = customer.mobile or customer.phone
        if not phone:
            return
        body = (
            f"Dear {customer.name},\n\n"
            f"🔧 Service Reminder for your *{vehicle.license_plate}* "
            f"({vehicle.brand} {vehicle.model}).\n\n"
            f"Recommended service date: *{reminder.predicted_date}*\n"
            f"{reminder.notes or ''}\n\n"
            f"Please call us to book your appointment.\n"
            f"📞 {self.garage_phone}\n"
            f"— {self.garage_name}"
        )
        self._send_message(phone, body)

    def send_vehicle_received(self, service_order):
        """Notify customer that vehicle has been received."""
        customer = service_order.customer_id
        vehicle = service_order.vehicle_id
        phone = customer.mobile or customer.phone
        if not phone:
            return
        body = (
            f"Dear {customer.name},\n\n"
            f"✅ We have received your vehicle *{vehicle.license_plate}* "
            f"({vehicle.brand} {vehicle.model}).\n\n"
            f"Job Card: {service_order.name}\n"
            f"We will notify you once the service is complete.\n\n"
            f"📞 {self.garage_phone}\n"
            f"— {self.garage_name}"
        )
        self._send_message(phone, body)

    def action_test_connection(self):
        """Test Twilio credentials."""
        url = f'https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}.json'
        try:
            response = requests.get(url, auth=(self.account_sid, self.auth_token), timeout=10)
            if response.status_code == 200:
                raise UserError('✅ Connection successful! Twilio credentials are valid.')
            else:
                raise UserError(f'❌ Connection failed. Status: {response.status_code}')
        except requests.exceptions.RequestException as e:
            raise UserError(f'❌ Connection error: {str(e)}')
