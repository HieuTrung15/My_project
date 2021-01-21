{
    "name": "Sales commissions",
    "depends": ["account", "product", "sale_management"],
    "website": "https://github.com/OCA/commission",
    "data": [
        "security/ir.model.access.csv",
        "views/sale_commission_view.xml",
        "views/sale_commission_mixin_views.xml",
        "views/product_template_view.xml",
        "views/res_partner_view.xml",
        "views/sale_order_view.xml",
        "views/account_move_views.xml",
        "views/sale_commission_settlement_view.xml",
        "wizard/wizard_settle.xml",
        "wizard/wizard_invoice.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
}
