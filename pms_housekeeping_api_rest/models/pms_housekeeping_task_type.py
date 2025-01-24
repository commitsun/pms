from odoo import models, fields, api
import uuid



class PmsHouseKeepingTaskType(models.Model):
    _inherit = "pms.housekeeping.task.type"

    housekeeping_uuid = fields.Char('Housekeeping UUID', required=True, copy=False, index=True)

    @api.model
    def create(self, vals):
        vals['housekeeping_uuid'] = str(uuid.uuid4())
        return super(PmsHouseKeepingTaskType, self).create(vals)
