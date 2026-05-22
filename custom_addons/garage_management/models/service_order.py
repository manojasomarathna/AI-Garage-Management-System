from odoo import models, fields, api
from odoo.exceptions import UserError


class GarageServiceOrder(models.Model):
    _name = 'garage.service.order'
    _description = 'Service Order / Job Card'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_received desc'

    name = fields.Char(string='Job Card No', readonly=True, default='New')
    vehicle_id = fields.Many2one('garage.vehicle', string='Vehicle', required=True, tracking=True)
    customer_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    mechanic_id = fields.Many2one('res.users', string='Assigned Mechanic', tracking=True)

    date_received = fields.Datetime(string='Date Received', default=fields.Datetime.now)
    date_promised = fields.Datetime(string='Promised Date')
    date_completed = fields.Datetime(string='Completed Date')

    mileage_in = fields.Integer(string='Mileage In (km)')
    mileage_out = fields.Integer(string='Mileage Out (km)')

    state = fields.Selection([
        ('draft', 'Received'),
        ('progress', 'In Progress'),
        ('quality', 'Quality Check'),
        ('ready', 'Ready for Pickup'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    service_line_ids = fields.One2many('garage.service.line', 'order_id', string='Services')
    parts_line_ids = fields.One2many('garage.parts.line', 'order_id', string='Parts Used')

    customer_complaint = fields.Text(string='Customer Complaint')
    diagnosis = fields.Text(string='Diagnosis')
    work_done = fields.Text(string='Work Done')

    labour_cost = fields.Float(string='Labour Cost', compute='_compute_totals', store=True)
    parts_cost = fields.Float(string='Parts Cost', compute='_compute_totals', store=True)
    total_amount = fields.Float(string='Total Amount', compute='_compute_totals', store=True)

    invoice_id = fields.Many2one('account.move', string='Invoice')
    is_invoiced = fields.Boolean(string='Invoiced', default=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('garage.service.order') or 'New'
        return super().create(vals_list)

    @api.depends('service_line_ids.subtotal', 'parts_line_ids.subtotal')
    def _compute_totals(self):
        for rec in self:
            rec.labour_cost = sum(rec.service_line_ids.mapped('subtotal'))
            rec.parts_cost = sum(rec.parts_line_ids.mapped('subtotal'))
            rec.total_amount = rec.labour_cost + rec.parts_cost

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        if self.vehicle_id:
            self.customer_id = self.vehicle_id.customer_id

    def action_start_progress(self):
        self.state = 'progress'

    def action_quality_check(self):
        self.state = 'quality'

    def action_ready(self):
        self.state = 'ready'
        self.date_completed = fields.Datetime.now()
        self.vehicle_id.last_service_date = fields.Date.today()
        if self.mileage_out:
            self.vehicle_id.last_service_mileage = self.mileage_out
        self._notify_customer_ready()
        self._create_service_history()

    def action_deliver(self):
        self.state = 'delivered'

    def action_cancel(self):
        if self.state == 'delivered':
            raise UserError('Cannot cancel a delivered order.')
        self.state = 'cancelled'

    def _notify_customer_ready(self):
        if 'garage.whatsapp' not in self.env:
            return
        whatsapp = self.env['garage.whatsapp'].search([], limit=1)
        if whatsapp:
            whatsapp.send_service_ready(self)

    def _create_service_history(self):
        self.env['garage.service.history'].create({
            'vehicle_id': self.vehicle_id.id,
            'service_order_id': self.id,
            'service_date': fields.Date.today(),
            'mileage': self.mileage_out or self.mileage_in,
            'work_summary': self.work_done,
            'total_cost': self.total_amount,
        })

    def action_create_invoice(self):
        if self.is_invoiced:
            raise UserError('Invoice already created.')
        invoice_lines = []
        for line in self.service_line_ids:
            invoice_lines.append((0, 0, {
                'name': line.service_name,
                'quantity': line.qty,
                'price_unit': line.unit_price,
            }))
        for line in self.parts_line_ids:
            invoice_lines.append((0, 0, {
                'name': line.product_id.name,
                'quantity': line.qty,
                'price_unit': line.unit_price,
            }))
        invoice = self.env['account.move'].sudo().create({
            'move_type': 'out_invoice',
            'partner_id': self.customer_id.id,
            'invoice_line_ids': invoice_lines,
            'narration': f'Job Card: {self.name}',
        })
        self.invoice_id = invoice.id
        self.is_invoiced = True
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
        }


class GarageServiceLine(models.Model):
    _name = 'garage.service.line'
    _description = 'Service Line'

    order_id = fields.Many2one('garage.service.order', string='Order')
    service_name = fields.Char(string='Service', required=True)
    description = fields.Char(string='Description')
    qty = fields.Float(string='Qty', default=1.0)
    unit_price = fields.Float(string='Unit Price')
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('qty', 'unit_price')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.qty * rec.unit_price


class GaragePartsLine(models.Model):
    _name = 'garage.parts.line'
    _description = 'Parts Line'

    order_id = fields.Many2one('garage.service.order', string='Order')
    product_id = fields.Many2one('product.product', string='Part', required=True)
    qty = fields.Float(string='Qty', default=1.0)
    unit_price = fields.Float(string='Unit Price')
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('qty', 'unit_price')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.qty * rec.unit_price

    @api.onchange('product_id')
    def _onchange_product(self):
        if self.product_id:
            self.unit_price = self.product_id.lst_price
