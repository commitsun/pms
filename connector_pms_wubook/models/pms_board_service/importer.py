# Copyright 2021 Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import Component


class ChannelWubookPmsBoardServiceDelayedBatchImporter(Component):
    _name = "channel.wubook.pms.board.service.delayed.batch.importer"
    _inherit = "channel.wubook.delayed.batch.importer"

    _apply_on = "channel.wubook.pms.board.service"


class ChannelWubookPmsBoardServiceDirectBatchImporter(Component):
    _name = "channel.wubook.pms.board.service.direct.batch.importer"
    _inherit = "channel.wubook.direct.batch.importer"

    _apply_on = "channel.wubook.pms.board.service"


class ChannelWubookPmsBoardServiceImporter(Component):
    _name = "channel.wubook.pms.board.service.importer"
    _inherit = "channel.wubook.importer"

    _apply_on = "channel.wubook.pms.board.service"

    def _mapper_options(self, binding):
        # TODO: remove this method override and use always the "binding" object
        # directly in the mapper doing all the lgic here directly on the mapper
        opts = super()._mapper_options(binding)
        if binding:
            return {"pms_properties_empty": bool(binding.pms_property_ids), **opts}
        return opts
