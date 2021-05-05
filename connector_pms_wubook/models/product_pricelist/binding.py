# Copyright 2021 Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ChannelWubookProductPriceBinding(models.Model):
    _name = "channel.wubook.product.pricelist"
    _inherit = "channel.wubook.binding"
    _inherits = {"product.pricelist": "odoo_id"}

    # binding fields
    odoo_id = fields.Many2one(
        comodel_name="product.pricelist",
        string="Odoo ID",
        required=True,
        ondelete="cascade",
    )

    @api.model
    def import_data(self, backend_id, date_from, date_to, pricelist_ids, room_type_ids):
        """ Prepare the batch import of Pricelists from Channel """
        domain = []
        if date_from and date_to:
            domain += [
                ("dfrom", "=", date_from),
                ("dto", "=", date_to),
            ]
        # TODO: duplicated code, unify
        if pricelist_ids:
            with backend_id.work_on(self._name) as work:
                binder = work.component(usage="binder")
            external_ids = []
            for pl in pricelist_ids:
                binding = binder.wrap_record(pl)
                if not binding or not binding.external_id:
                    raise NotImplementedError(
                        _(
                            "The pricelist %s has no binding. Import of Odoo records "
                            "without binding is not supported yet"
                        )
                        % pl.name
                    )
                external_ids.append(binding.external_id)
            domain.append(("id", "in", external_ids))
        if room_type_ids:
            with backend_id.work_on("channel.wubook.pms.room.type") as work:
                binder = work.component(usage="binder")
            external_ids = []
            for rt in room_type_ids:
                binding = binder.wrap_record(rt)
                if not binding or not binding.external_id:
                    raise NotImplementedError(
                        _(
                            "The Room type %s has no binding. Import of Odoo records "
                            "without binding is not supported yet"
                        )
                        % pl.name
                    )
                external_ids.append(binding.external_id)
            domain.append(("rooms", "in", external_ids))
        return self.import_batch(backend_record=backend_id, domain=domain)

    def write(self, values):
        # workaround to surpass an Odoo bug in a delegation inheritance
        # of product.pricelist that does not let to write 'name' field
        # if 'items_ids' is written as well on the same write call.
        # With other fields like 'sequence' it does not crash but it does not
        # save the value entered. For other fields it works but it's unstable.
        item_ids = values.pop("item_ids", None)
        if item_ids:
            super(ChannelWubookProductPriceBinding, self).write({"item_ids": item_ids})
        if values:
            return super(ChannelWubookProductPriceBinding, self).write(values)
