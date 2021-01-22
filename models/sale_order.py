from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line.agent_ids.amount')
    def _compute_commission_total(self):
        for record in self:
            record.commission_total = sum(record.mapped('order_line.agent_ids.amount'))

    commission_total = fields.Float(string='Commissions', compute='_compute_commission_total', store=True)


class SaleOrderLine(models.Model):
    _inherit = [
        'sale.order.line',
        'sale.commission.mixin',
    ]
    _name = 'sale.order.line'

    agent_ids = fields.One2many('sale.order.line.agent')


class SaleOrderLineAgent(models.Model):
    _inherit = 'sale.commission.line.mixin'
    _name = 'sale.order.line.agent'
    _description = "Chi tiet dai ly cua tung dong hoa hong trong orderline"

    object_id = fields.Many2one('sale.order.line')
    currency_id = fields.Many2one(related='object_id.currency_id')

    @api.depends('object_id.price_subtotal', 'object_id.product_id', 'object_id.product_uom_qty')
    def _compute_amount(self):
        for line in self:
            order_line = line.object_id
            line.amount = line._get_commission_amount(
                line.commission_id,
                order_line.price_subtotal,
                order_line.product_id,
                order_line.product_uom_qty,
            )
