# Copyright 2021 Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class ChannelWubookProductPricelistDelayedBatchImporter(Component):
    _name = "channel.wubook.product.pricelist.delayed.batch.importer"
    _inherit = "channel.wubook.delayed.batch.importer"

    _apply_on = "channel.wubook.product.pricelist"


class ChannelWubookProductPricelistDirectBatchImporter(Component):
    _name = "channel.wubook.product.pricelist.direct.batch.importer"
    _inherit = "channel.wubook.direct.batch.importer"

    _apply_on = "channel.wubook.product.pricelist"


class ChannelWubookProductPricelistImporter(Component):
    _name = "channel.wubook.product.pricelist.importer"
    _inherit = "channel.wubook.importer"

    _apply_on = "channel.wubook.product.pricelist"

    def _import_dependencies(self, external_data):
        for it in external_data.get("items", []):
            if it["type"] == "pricelist":
                self._import_dependency(it["vpid"], "channel.wubook.product.pricelist")
            elif it["type"] == "room":
                self._import_dependency(it["rid"], "channel.wubook.pms.room.type")
            else:
                raise ValidationError(_("Pricelist type %s not valid") % it["type"])
