from odoo import fields, models, api
import uuid


class ResUsers(models.Model):
    _inherit = "res.users"

    housekeeping_uuid = fields.Char('Housekeeping UUID', required=True, copy=False, index=True)

    user_role = fields.Selection(
        selection=[
            ("housekeeper", "Housekeeper"),
            ("housekeeping_manager", "Housekeeping Manager")
        ],
        string="User Role",
    )

    @api.model
    def create(self, vals):
        vals['housekeeping_uuid'] = str(uuid.uuid4())
        return super(ResUsers, self).create(vals)
