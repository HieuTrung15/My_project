from odoo import _, api, fields, models


class SaleCommissionMixin(models.Model):
    _name = "sale.commission.mixin"

    agent_ids = fields.One2many("sale.commission.line.mixin", inverse_name="object_id", string="Agents & commissions",
                                store=True)
    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    commission_free = fields.Boolean(string="Commission free", related="product_id.commission_free", store=True)
    commission_status = fields.Char(compute="_compute_commission_status", string="Commission")

    @api.depends("commission_free", "agent_ids")
    def _compute_commission_status(self):
        for line in self:
            if len(line.agent_ids) == 0:
                line.commission_status = _("No commission agents")
            else:
                line.commission_status = _("%s commission agents") % (len(line.agent_ids))

    def button_edit_agents(self):
        self.ensure_one()
        view = self.env.ref("sale_commission.view_sale_commission_mixin_agent_only")
        return {
            "name": _("Agents"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": self._name,
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": self.id,
            "context": self.env.context,
        }


class SaleCommissionLineMixin(models.Model):
    _name = 'sale.commission.line.mixin'
    _sql_constraints = [(
            "unique_agent",
            "UNIQUE(object_id, agent_id)",
            "You can only add one time each agent.",
        )]

    object_id = fields.Many2one("sale.commission.mixin",ondelete="cascade",required=True,string="Parent")
    agent_id = fields.Many2one("res.partner", domain="[('agent', '=', True)]", required=True)
    commission_id = fields.Many2one("sale.commission", ondelete="restrict", required=True,
        compute="_compute_commission_id", store=True,readonly=False)
    amount = fields.Monetary(string="Commission Amount", compute="_compute_amount", store=True)

    currency_id = fields.Many2one(comodel_name="res.currency")

    # def _compute_amount(self):
    #     raise NotImplementedError()

    def _get_commission_amount(self, commission, subtotal, product, quantity):

        self.ensure_one()
        if product.commission_free or not commission:
            return 0.0
        if commission.amount_base_type == "net_amount":
            subtotal = max([0, subtotal - product.standard_price * quantity])
        if commission.commission_type == "fixed":
            return subtotal * (commission.fix_qty / 100.0)
        elif commission.commission_type == "section":
            return commission.calculate_section(subtotal)

    @api.depends("agent_id")
    def _compute_commission_id(self):
        for record in self:
            record.commission_id = record.agent_id.commission_id
