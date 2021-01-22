from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    agent_ids = fields.Many2many('res.partner', relation='partner_agent_rel', column1="partner_id",
    column2="agent_id", domain=[("agent", "=", True)], string="Agents")

    agent = fields.Boolean(string='Creditor/Agent')
    agent_type = fields.Selection(selection=[("agent", "External agent")], string="Type", default="agent")
    commission_id = fields.Many2one('sale.commission', string="Commission")
    settlement = fields.Selection([
            ("monthly", "Monthly"),
            ("quaterly", "Quarterly"),
            ("semi", "Semi-annual"),
            ("annual", "Annual"),
        ],
        string="Settlement period",
        default="monthly")
    settlement_ids = fields.One2many('sale.commission.settlement', 'agent_id')

