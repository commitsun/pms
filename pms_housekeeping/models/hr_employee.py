# Copyright 2020 Jose Luis Algara (Alda Hotels <https://www.aldahotels.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import uuid


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    pre_assigned_room_ids = fields.Many2many(
        comodel_name="pms.room",
        string="Pre Assigned Rooms",
        help="Rooms pre assigned to this employee",
    )

    allowed_pre_assigned_room_ids = fields.Many2many(
        comodel_name="pms.room",
        string="Allowed Pre Assigned Rooms",
        help="Rooms allowed to be pre assigned to this employee",
        compute="_compute_allowed_pre_assigned_room_ids",
    )

    is_housekeeping_job = fields.Boolean(
        string="Is Housekeeping Job",
        related="job_id.is_housekeeping_job",
        store=True,
    )

    @api.constrains("pre_assigned_room_ids")
    def _check_pre_assigned_room_ids(self):
        for record in self:
            if record.pre_assigned_room_ids:
                for room in record.pre_assigned_room_ids:
                    if room not in record.allowed_pre_assigned_room_ids:
                        raise ValidationError(
                            _("The room should belong to the employee's property.")
                        )

    @api.constrains("pre_assigned_room_ids")
    def _check_job_id(self):
        for record in self:
            if (
                record.job_id
                and record.job_id
                != self.env.ref("pms_housekeeping.housekeeping_job_id")
                and record.pre_assigned_room_ids
            ):
                raise ValidationError(_("The job position should be Housekeeper."))

    @api.depends("property_ids")
    def _compute_allowed_pre_assigned_room_ids(self):
        for record in self:
            domain = []
            if record.property_ids:
                domain.append(("pms_property_id", "in", record.property_ids.ids))
            record.allowed_pre_assigned_room_ids = (
                self.env["pms.room"].search(domain).ids
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "uuid" not in vals:
                vals["uuid"] = str(uuid.uuid4())
        return super().create(vals_list)
