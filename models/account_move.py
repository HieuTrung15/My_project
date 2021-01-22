from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    commission_total = fields.Float(string="Commissions", compute='_compute_commission_total', store=True, )
    settlement_id = fields.Many2one('sale.commission.settlement')

    @api.depends('line_ids.agent_ids.amount')
    def _compute_commission_total(self):
        for record in self:
            record.commission_total = 0.0
            for line in record.line_ids:
                record.commission_total += sum(x.amount for x in line.agent_ids)


class AccountMoveLine(models.Model):
    _inherit = ['account.move.line', 'sale.commission.mixin']
    _name = 'account.move.line'

    agent_ids = fields.One2many('account.invoice.line.agent', 'object_id')
    any_settled = fields.Boolean(compute='_compute_any_settled')

    @api.depends('agent_ids', 'agent_ids.settled')
    def _compute_any_settled(self):
        for record in self:
            record.any_settled = any(record.mapped('agent_ids.settled'))


class AccountInvoiceLineAgent(models.Model):
    _inherit = 'sale.commission.line.mixin'
    _name = 'account.invoice.line.agent'

    object_id = fields.Many2one('account.move.line')
    invoice_id = fields.Many2one("account.move", string="Invoice", related="object_id.move_id", )
    invoice_date = fields.Date(string="Invoice date", related="invoice_id.date")
    agent_line = fields.Many2many("sale.commission.settlement.line", relation="settlement_agent_line_rel",
                                  column1="agent_line_id", column2="settlement_id")
    settled = fields.Boolean(compute="_compute_settled", store=True)
    company_id = fields.Many2one(comodel_name="res.company", compute="_compute_company", store=True)
    currency_id = fields.Many2one(related="object_id.currency_id", readonly=True)

    @api.depends("object_id.price_subtotal", "object_id.product_id.commission_free")
    def _compute_amount(self):
        for line in self:
            inv_line = line.object_id
            line.amount = line._get_commission_amount(
                line.commission_id,
                inv_line.price_subtotal,
                inv_line.product_id,
                inv_line.quantity,
            )

    @api.depends("agent_line", "agent_line.settlement_id.state", "invoice_id", "invoice_id.state")
    def _compute_settled(self):
        for line in self:
            line.settled = any(
                x.settlement_id.state != "cancel" for x in line.agent_line
            )

    @api.depends("object_id", "object_id.company_id")
    def _compute_company(self):
        for line in self:
            line.company_id = line.object_id.company_id

    def _skip_settlement(self):
        self.ensure_one()
        return (self.commission_id.invoice_state == "paid" and self.invoice_id.invoice_payment_state != "paid") or self.invoice_id.state != "posted"
