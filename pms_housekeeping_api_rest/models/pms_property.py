from odoo import fields, models, api
import uuid

class PmsProperty(models.Model):
    _inherit = "pms.property"

    housekeeping_uuid = fields.Char('Housekeeping UUID', required=True, copy=False, index=True)

    hotel_image_pms_api_rest = fields.Image(
        string="Hotel image",
        store=True,
    )

    @api.model
    def create(self, vals):
        vals['housekeeping_uuid'] = str(uuid.uuid4())
        return super(PmsProperty, self).create(vals)
