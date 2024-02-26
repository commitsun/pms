from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    availability_rule_field_ids = fields.Many2many(
        string="Availability Rules",
        help="Configurable availability rules",
        comodel_name="ir.model.fields",
        default=lambda self: self._get_default_avail_rule_fields(),
        relation="ir_model_fields_res_users_rel",
        column1="ir_model_fields",
        column2="res_users",
    )

    is_new_interface_app_user = fields.Boolean(
        string="Is New Interface App User",
        help="Is New Interface App User",
        default=False,
        store=True,
        readonly=False,
    )
    pms_api_client = fields.Boolean(
        string="PMS API Client",
        help="PMS API Client",
    )
    url_endpoint_prices = fields.Char(
        string="URL Endpoint Prices",
        help="URL Endpoint Prices",
    )
    url_endpoint_availability = fields.Char(
        string="URL Endpoint Availability",
        help="URL Endpoint Availability",
    )
    url_endpoint_rules = fields.Char(
        string="URL Endpoint Rules",
        help="URL Endpoint Rules",
    )
    external_public_token = fields.Char(
        string="External Public Token",
        help="External Public Token",
    )
    main_avail_plan_id = fields.Many2one(
        string="Main Availability Plan",
        help="Main Availability Plan",
        comodel_name="pms.availability.plan",
    )
    main_pricelist_id = fields.Many2one(
        string="Main Pricelist",
        help="Main Pricelist",
        comodel_name="product.pricelist",
    )
    excluded_room_type_ids = fields.Many2many(
        string="Excluded Room Types",
        help="Excluded Room Types",
        comodel_name="pms.room.type",
    )

    def _get_default_avail_rule_fields(self):
        default_avail_rule_fields = self.env["ir.model.fields"].search(
            [
                ("model_id", "=", "pms.availability.plan.rule"),
                ("name", "in", ("min_stay", "quota")),
            ]
        )
        if default_avail_rule_fields:
            return default_avail_rule_fields.ids
        else:
            return []
