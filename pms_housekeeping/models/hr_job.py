from odoo import fields, models, api


class HrJob(models.Model):
    _inherit = "hr.job"

    is_housekeeping_job = fields.Boolean(string="Is using in Housekeeping", default=False)
