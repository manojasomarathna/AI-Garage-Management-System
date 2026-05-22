from odoo import models, fields, api
from odoo.exceptions import ValidationError


class GarageVehicle(models.Model):
    _name = 'garage.vehicle'
    _description = 'Vehicle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'license_plate'

    license_plate = fields.Char(string='License Plate', required=True, tracking=True)
    brand = fields.Char(string='Brand', required=True)
    model = fields.Char(string='Model', required=True)
    year = fields.Integer(string='Year')
    color = fields.Char(string='Color')
    vin = fields.Char(string='VIN / Chassis No')
    fuel_type = fields.Selection([
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('hybrid', 'Hybrid'),
        ('electric', 'Electric'),
    ], string='Fuel Type', default='petrol')
    vehicle_type = fields.Selection([
        ('car', 'Car'),
        ('van', 'Van'),
        ('suv', 'SUV'),
        ('truck', 'Truck'),
        ('motorcycle', 'Motorcycle'),
        ('three_wheel', 'Three Wheeler'),
    ], string='Vehicle Type', default='car')

    customer_id = fields.Many2one('res.partner', string='Owner', required=True, tracking=True)
    current_mileage = fields.Integer(string='Current Mileage (km)')
    last_service_date = fields.Date(string='Last Service Date')
    last_service_mileage = fields.Integer(string='Last Service Mileage (km)')

    service_order_ids = fields.One2many('garage.service.order', 'vehicle_id', string='Service Orders')
    service_count = fields.Integer(string='Service Count', compute='_compute_service_count')
    reminder_ids = fields.One2many('garage.reminder', 'vehicle_id', string='Reminders')

    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True)

    @api.depends('service_order_ids')
    def _compute_service_count(self):
        for rec in self:
            rec.service_count = len(rec.service_order_ids)

    @api.constrains('year')
    def _check_year(self):
        for rec in self:
            if rec.year and (rec.year < 1900 or rec.year > 2100):
                raise ValidationError('Please enter a valid year.')

    def action_view_service_orders(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Service Orders',
            'res_model': 'garage.service.order',
            'view_mode': 'list,form',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id},
        }

    def action_create_service_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Service Order',
            'res_model': 'garage.service.order',
            'view_mode': 'form',
            'context': {
                'default_vehicle_id': self.id,
                'default_customer_id': self.customer_id.id,
            },
        }
