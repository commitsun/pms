from odoo import fields, models, api
import uuid

class PmsReservation(models.Model):
    _inherit = "pms.reservation"

    housekeeping_uuid = fields.Char('UUID', required=True, copy=False, index=True)

    @api.model
    def create(self, vals):
        vals['housekeeping_uuid'] = str(uuid.uuid4())
        return super(PmsReservation, self).create(vals)
