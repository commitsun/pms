# Copyright 2021 Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression


class PmsFolio(models.Model):
    _inherit = "pms.folio"

    channel_wubook_bind_ids = fields.One2many(
        comodel_name="channel.wubook.pms.folio",
        inverse_name="odoo_id",
        string="Channel Wubook PMS Bindings",
    )

    reservation_origin_code = fields.Integer(
        string="Reservation Origin Code",
    )

    @api.model
    def _name_search(
        self, name="", args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = args or []
        domain = []
        if name:
            domain = [
                "|",
                ("name", operator, name),
                ("reservation_origin_code", operator, name),
                ("channel_wubook_bind_ids.external_id", operator, name),
            ]
        return self._search(
            expression.AND([domain + args]), limit=limit, access_rights_uid=name_get_uid
        )
