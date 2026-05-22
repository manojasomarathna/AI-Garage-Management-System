from odoo import models, fields


class GarageServiceHistory(models.Model):
    _name = 'garage.service.history'
    _description = 'Service History'
    _order = 'service_date desc'

    vehicle_id = fields.Many2one('garage.vehicle', string='Vehicle', required=True)
    service_order_id = fields.Many2one('garage.service.order', string='Job Card')
    customer_id = fields.Many2one(related='vehicle_id.customer_id', string='Customer', store=True)

    service_date = fields.Date(string='Service Date', required=True)
    mileage = fields.Integer(string='Mileage (km)')
    work_summary = fields.Text(string='Work Done')
    total_cost = fields.Float(string='Total Cost')

    parts_replaced = fields.Text(string='Parts Replaced')
    next_service_date = fields.Date(string='Recommended Next Service')
    next_service_mileage = fields.Integer(string='Next Service Mileage (km)')
