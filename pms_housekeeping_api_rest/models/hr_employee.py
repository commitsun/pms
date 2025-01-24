from odoo import fields, models, api
import uuid


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    housekeeping_uuid = fields.Char('Housekeeping UUID', required=True, copy=False, index=True)

    @api.model
    def create(self, vals):
        vals['housekeeping_uuid'] = str(uuid.uuid4())
        return super(HrEmployee, self).create(vals)

