# Copyright 2017  Alexandre Díaz, Pablo Quesada, Darío Lodeiros
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ProductPricelist(models.Model):
    """Before creating a 'daily' pricelist, you need to consider the following:
    A pricelist marked as daily is used as a daily rate plan for room types and
    therefore is related only with one property.
    """

    _inherit = "product.pricelist"

    # Fields declaration
    pms_property_ids = fields.Many2many(
        "pms.property", string="Properties", required=False, ondelete="restrict"
    )
    cancelation_rule_id = fields.Many2one(
        "pms.cancelation.rule",
        string="Cancelation Policy",
        domain=[
            "|",
            ("pms_property_ids", "=", False),
            ("pms_property_ids", "in", pms_property_ids),
        ],
    )
    pricelist_type = fields.Selection(
        [("daily", "Daily Plan")], string="Pricelist Type", default="daily"
    )
    pms_sale_channel_ids = fields.Many2many(
        "pms.sale.channel", string="Available Channels"
    )

    availability_plan_id = fields.Many2one(
        comodel_name="pms.room.type.availability.plan",
        string="Availability Plan",
        ondelete="restrict",
        domain=[
            "|",
            ("pms_property_ids", "=", False),
            ("pms_property_ids", "in", pms_property_ids),
        ],
    )

    # Constraints and onchanges
    # @api.constrains("pricelist_type", "pms_property_ids")
    # def _check_pricelist_type_property_ids(self):
    #     for record in self:
    #         if record.pricelist_type == "daily" and len(record.pms_property_ids) != 1:
    #             raise ValidationError(
    #                 _(
    #                     "A daily pricelist is used as a daily Rate Plan "
    #                     "for room types and therefore must be related with "
    #                     "one and only one property."
    #                 )
    #             )

    #         if record.pricelist_type == "daily" and len(record.pms_property_ids) == 1:
    #             pms_property_id = (
    #                 self.env["pms.property"].search(
    #                     [("default_pricelist_id", "=", record.id)]
    #                 )
    #                 or None
    #             )
    #             if pms_property_id and pms_property_id != record.pms_property_ids:
    #                 raise ValidationError(
    #                     _("Relationship mismatch.")
    #                     + " "
    #                     + _(
    #                         "This pricelist is used as default in a "
    #                         "different property."
    #                     )
    #                 )

    def _compute_price_rule_get_items(
        self, products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids
    ):
        if (
            "property" in self._context
            and self._context["property"]
            and self._context.get("date_overnight")
        ):
            # board_service_id = self._context.get("board_service")
            # on_board_service_bool = True if board_service_id else False
            # self.env["product.pricelist.item"].flush(
            #     ["price", "currency_id", "company_id"]
            # )
            self.env.cr.execute(
                """
                SELECT item.id
                FROM   product_pricelist_item item
                       LEFT JOIN product_category categ
                            ON item.categ_id = categ.id
                       LEFT JOIN pms_property_product_pricelist_rel cab
                            ON item.pricelist_id = cab.product_pricelist_id
                       LEFT JOIN pms_property_product_pricelist_item_rel lin
                            ON item.id = lin.product_pricelist_item_id
                       LEFT JOIN board_service_pricelist_item_rel board
                            ON item.id = board.pricelist_item_id
                WHERE  (lin.pms_property_id = %s OR lin.pms_property_id IS NULL)
                   AND (cab.pms_property_id = %s OR cab.pms_property_id IS NULL)
                   AND (item.product_tmpl_id IS NULL
                        OR item.product_tmpl_id = ANY(%s))
                   AND (item.product_id IS NULL OR item.product_id = ANY(%s))
                   AND (item.categ_id IS NULL OR item.categ_id = ANY(%s))
                   AND (item.pricelist_id = %s)
                   AND (item.date_start IS NULL OR item.date_start <=%s)
                   AND (item.date_end IS NULL OR item.date_end >=%s)
                   AND (item.date_start_overnight IS NULL
                        OR item.date_start_overnight <=%s)
                   AND (item.date_end_overnight IS NULL
                        OR item.date_end_overnight >=%s)
                GROUP  BY item.id
                ORDER  BY item.applied_on,
                          /* REVIEW: priotrity date sale / date overnight */
                          item.date_end - item.date_start ASC,
                          item.date_end_overnight - item.date_start_overnight ASC,
                          NULLIF((SELECT COUNT(1)
                           FROM   pms_property_product_pricelist_item_rel l
                           WHERE  item.id = l.product_pricelist_item_id)
                          + (SELECT COUNT(1)
                             FROM   pms_property_product_pricelist_rel c
                             WHERE  item.pricelist_id = c.product_pricelist_id),0)
                          NULLS LAST,
                          item.id DESC;
                """,
                (
                    self._context["property"],
                    self._context["property"],
                    prod_tmpl_ids,
                    prod_ids,
                    categ_ids,
                    # on_board_service_bool,
                    # board_service_id,
                    self.id,
                    date,
                    date,
                    self._context["date_overnight"],
                    self._context["date_overnight"],
                ),
            )

            item_ids = [x[0] for x in self.env.cr.fetchall()]
            items = self.env["product.pricelist.item"].browse(item_ids)
        else:
            items = super(ProductPricelist, self)._compute_price_rule_get_items(
                products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids
            )
        return items

    # Action methods
    def open_massive_changes_wizard(self):

        if self.ensure_one():
            return {
                "view_type": "form",
                "view_mode": "form",
                "name": "Massive changes on Pricelist: " + self.name,
                "res_model": "pms.massive.changes.wizard",
                "target": "new",
                "type": "ir.actions.act_window",
                "context": {
                    "pricelist_id": self.id,
                },
            }

    @api.constrains(
        "cancelation_rule_id",
    )
    def _check_property_integrity(self):
        for rec in self:
            if rec.pms_property_ids:
                for p in rec.pms_property_ids:
                    if p.id not in rec.cancelation_rule_id.pms_property_ids.ids:
                        raise ValidationError(
                            _("Property not allowed in cancelation rule")
                        )

    @api.constrains("pms_property_ids", "availability_plan_id")
    def _check_availability_plan_property_integrity(self):
        for record in self:
            if record.pms_property_ids and record.availability_plan_id.pms_property_ids:
                for pms_property in record.pms_property_ids:
                    if pms_property not in record.availability_plan_id.pms_property_ids:
                        raise ValidationError(
                            _("Property not allowed availability plan")
                        )
