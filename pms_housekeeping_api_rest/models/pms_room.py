from odoo import fields, models, api
import uuid



class PmsRoom(models.Model):
    _inherit = "pms.room"

    housekeeping_uuid = fields.Char('Housekeeping UUID', required=True, copy=False, index=True)

    @api.model
    def create(self, vals):
        vals['housekeeping_uuid'] = str(uuid.uuid4())
        return super(PmsRoom, self).create(vals)
