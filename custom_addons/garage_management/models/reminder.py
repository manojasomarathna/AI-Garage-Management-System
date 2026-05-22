from odoo import models, fields, api
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)

# Service interval rules by vehicle type (days, km)
SERVICE_INTERVALS = {
    'car':         {'days': 90,  'km': 5000},
    'van':         {'days': 60,  'km': 4000},
    'suv':         {'days': 90,  'km': 5000},
    'truck':       {'days': 45,  'km': 3000},
    'motorcycle':  {'days': 60,  'km': 3000},
    'three_wheel': {'days': 60,  'km': 3000},
}


class GarageReminder(models.Model):
    _name = 'garage.reminder'
    _description = 'AI Service Reminder'
    _order = 'predicted_date asc'

    vehicle_id = fields.Many2one('garage.vehicle', string='Vehicle', required=True)
    customer_id = fields.Many2one(related='vehicle_id.customer_id', string='Customer', store=True)

    predicted_date = fields.Date(string='Predicted Service Date')
    predicted_mileage = fields.Integer(string='Predicted Service Mileage (km)')
    reminder_type = fields.Selection([
        ('oil_change', 'Oil Change'),
        ('full_service', 'Full Service'),
        ('tyre_rotation', 'Tyre Rotation'),
        ('brake_check', 'Brake Check'),
        ('general', 'General Service'),
    ], string='Reminder Type', default='general')

    state = fields.Selection([
        ('pending', 'Pending'),
        ('sent', 'Notification Sent'),
        ('booked', 'Booked'),
        ('done', 'Done'),
        ('ignored', 'Ignored'),
    ], string='Status', default='pending')

    notification_sent_date = fields.Date(string='Notification Sent On')
    notes = fields.Text(string='AI Notes')

    @api.model
    def generate_reminders(self):
        """Cron job: AI generates reminders for all vehicles."""
        vehicles = self.env['garage.vehicle'].search([('active', '=', True)])
        created = 0
        for vehicle in vehicles:
            if not vehicle.last_service_date:
                continue
            existing = self.search([
                ('vehicle_id', '=', vehicle.id),
                ('state', 'in', ['pending', 'sent']),
            ])
            if existing:
                continue
            predicted_date, notes = self._predict_next_service(vehicle)
            self.create({
                'vehicle_id': vehicle.id,
                'predicted_date': predicted_date,
                'notes': notes,
            })
            created += 1
        _logger.info('AI Garage: Generated %d service reminders.', created)

    def _predict_next_service(self, vehicle):
        """Core AI prediction logic based on vehicle type and usage pattern."""
        v_type = vehicle.vehicle_type or 'car'
        interval = SERVICE_INTERVALS.get(v_type, SERVICE_INTERVALS['car'])

        # Adjust interval based on mileage-driven usage pattern
        avg_daily_km = self._estimate_daily_km(vehicle)
        if avg_daily_km > 80:
            days = int(interval['days'] * 0.75)   # High usage → earlier service
            note = 'High daily usage detected. Earlier service recommended.'
        elif avg_daily_km < 20:
            days = int(interval['days'] * 1.25)   # Low usage → later service
            note = 'Low daily usage detected. Extended service interval applied.'
        else:
            days = interval['days']
            note = 'Normal usage pattern. Standard service interval applied.'

        predicted_date = vehicle.last_service_date + timedelta(days=days)
        return predicted_date, note

    def _estimate_daily_km(self, vehicle):
        """Estimate average daily km from service history."""
        history = self.env['garage.service.history'].search(
            [('vehicle_id', '=', vehicle.id)],
            order='service_date desc',
            limit=3,
        )
        if len(history) < 2:
            return 40  # Default assumption

        km_diffs, day_diffs = [], []
        records = list(history)
        for i in range(len(records) - 1):
            km_diff = records[i].mileage - records[i + 1].mileage
            day_diff = (records[i].service_date - records[i + 1].service_date).days
            if day_diff > 0 and km_diff > 0:
                km_diffs.append(km_diff)
                day_diffs.append(day_diff)

        if not day_diffs:
            return 40
        total_km = sum(km_diffs)
        total_days = sum(day_diffs)
        return total_km / total_days

    @api.model
    def send_pending_reminders(self):
        """Cron job: Send WhatsApp notifications for due reminders."""
        today = fields.Date.today()
        due_reminders = self.search([
            ('state', '=', 'pending'),
            ('predicted_date', '<=', today + timedelta(days=7)),
        ])
        for reminder in due_reminders:
            try:
                whatsapp = self.env['garage.whatsapp'].search([], limit=1)
                if whatsapp:
                    whatsapp.send_service_reminder(reminder)
                reminder.state = 'sent'
                reminder.notification_sent_date = today
            except Exception as e:
                _logger.error('Failed to send reminder for vehicle %s: %s',
                              reminder.vehicle_id.license_plate, str(e))
