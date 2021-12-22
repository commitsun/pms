# Copyright 2017  Dario Lodeiros
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PmsBoardServiceLine(models.Model):
    _name = "pms.board.service.line"
    _description = "Services on Board Service included"
    _check_pms_properties_auto = True

    pms_board_service_id = fields.Many2one(
        string="Board Service",
        help="Board Service in which this line is included",
        required=True,
        comodel_name="pms.board.service",
        ondelete="cascade",
        check_pms_properties=True,
    )
    product_id = fields.Many2one(
        string="Product",
        help="Product associated with this board service line",
        required=True,
        comodel_name="product.product",
        check_pms_properties=True,
    )
    pms_property_ids = fields.Many2many(
        string="Properties",
        help="Properties with access to the element;"
        " if not set, all properties can access",
        comodel_name="pms.property",
        relation="pms_board_service_line_pms_property_rel",
        column1="pms_board_service_line_id",
        column2="pms_property_id",
        store=True,
        check_pms_properties=True,
    )
    amount = fields.Float(
        string="Amount",
        help="Price for this Board Service Line/Product",
        default=lambda self: self._get_default_price(),
        compute="_compute_amount",
        inverse="_inverse_ir_pms_property",
        digits=("Product Price"),
    )

    def _get_default_price(self):
        if self.product_id:
            return self.product_id.list_price

    @api.depends_context("allowed_pms_property_ids")
    # @api.depends("pms_property_ids")
    def _compute_amount(self):
        for record in self:
            pms_property_id = self.env.user.get_active_property_ids()[0]
            if pms_property_id:
                model_id = self.env["ir.model"].browse(self._name).id
                model = self.env["ir.model"].search([("model", "=", model_id)])
                if model:
                    field_id = self.env["ir.model.fields"].search(
                        [("name", "=", "amount"), ("model_id", "=", model.id)]
                    )
                    ir_pms_property = self.env["ir.pms.property"].search(
                        [
                            ("pms_property_id", "=", pms_property_id),
                            ("field_id", "=", field_id[0].id),
                            ("record", "=", record.id),
                        ]
                    )
                    if ir_pms_property:
                        record.amount = ir_pms_property.value_float

    def _inverse_ir_pms_property(self):
        for record in self:
            pms_property_id = self.env.user.get_active_property_ids()[0]
            if pms_property_id:
                model_id = self.env["ir.model"].browse(self._name).id
                model = self.env["ir.model"].search([("model", "=", model_id)])
                if model:
                    field_id = self.env["ir.model.fields"].search(
                        [("name", "=", "amount"), ("model_id", "=", model.id)]
                    )
                    ir_pms_property = self.env["ir.pms.property"].search(
                        [
                            ("pms_property_id", "=", pms_property_id),
                            ("field_id", "=", field_id[0].id),
                            ("record", "=", record.id),
                        ]
                    )
                    if ir_pms_property:
                        ir_pms_property.value_float = record.amount
                    else:
                        self.env["ir.pms.property"].create(
                            {
                                "pms_property_id": pms_property_id,
                                "model_id": model.id,
                                "field_id": field_id[0].id,
                                "value_float": record.amount,
                                "record": record.id,
                            }
                        )

    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            self.update({"amount": self.product_id.list_price})

    @api.model
    def create(self, vals):
        properties = False
        if "pms_board_service_id" in vals:
            board_service = self.env["pms.board.service"].browse(
                vals["pms_board_service_id"]
            )
            properties = board_service.pms_property_ids
        if properties:
            vals.update(
                {
                    "pms_property_ids": properties,
                }
            )
        return super(PmsBoardServiceLine, self).create(vals)

    def write(self, vals):
        properties = False
        if "pms_board_service_id" in vals:
            board_service = self.env["pms.board.service"].browse(
                vals["pms_board_service_id"]
            )
            properties = board_service.pms_property_ids
        if properties:
            vals.update(
                {
                    "pms_property_ids": properties,
                }
            )
        return super(PmsBoardServiceLine, self).write(vals)
