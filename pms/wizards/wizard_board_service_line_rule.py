# Copyright 2026  Dario Lodeiros
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class PmsBoardServiceLineRuleWizard(models.TransientModel):
    _name = "pms.board.service.line.rule.wizard"
    _description = "Board Service Line Rule Wizard"

    board_service_id = fields.Many2one(
        string="Board Service",
        comodel_name="pms.board.service",
        required=True,
    )
    available_property_ids = fields.Many2many(
        comodel_name="pms.property",
        compute="_compute_available_properties",
    )
    pms_property_ids = fields.Many2many(
        string="Properties",
        comodel_name="pms.property",
        help="Filter board service room types by property.",
    )
    available_room_type_ids = fields.Many2many(
        comodel_name="pms.room.type",
        compute="_compute_available_room_types",
    )
    room_type_ids = fields.Many2many(
        string="Room Types",
        comodel_name="pms.room.type",
        help="Filter board service room types by room type.",
    )
    amount = fields.Float(
        string="Rule Price",
        required=True,
        digits=("Product Price"),
    )
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")

    weekday_monday = fields.Boolean(string="Monday", default=True)
    weekday_tuesday = fields.Boolean(string="Tuesday", default=True)
    weekday_wednesday = fields.Boolean(string="Wednesday", default=True)
    weekday_thursday = fields.Boolean(string="Thursday", default=True)
    weekday_friday = fields.Boolean(string="Friday", default=True)
    weekday_saturday = fields.Boolean(string="Saturday", default=True)
    weekday_sunday = fields.Boolean(string="Sunday", default=True)

    @api.depends("board_service_id")
    def _compute_available_properties(self):
        board_service_room_type = self.env["pms.board.service.room.type"]
        all_properties = self.env["pms.property"]
        for wizard in self:
            if not wizard.board_service_id:
                wizard.available_property_ids = False
                continue
            bs_room_types = board_service_room_type.search(
                [("pms_board_service_id", "=", wizard.board_service_id.id)]
            )
            if not bs_room_types:
                wizard.available_property_ids = False
                continue
            if any(not rec.pms_property_id for rec in bs_room_types):
                wizard.available_property_ids = all_properties.search([])
            else:
                wizard.available_property_ids = bs_room_types.mapped("pms_property_id")

    @api.depends("board_service_id", "pms_property_ids")
    def _compute_available_room_types(self):
        board_service_room_type = self.env["pms.board.service.room.type"]
        for wizard in self:
            if not wizard.board_service_id:
                wizard.available_room_type_ids = False
                continue
            domain = [("pms_board_service_id", "=", wizard.board_service_id.id)]
            if wizard.pms_property_ids:
                domain.extend(
                    [
                        "|",
                        ("pms_property_id", "=", False),
                        ("pms_property_id", "in", wizard.pms_property_ids.ids),
                    ]
                )
            bs_room_types = board_service_room_type.search(domain)
            wizard.available_room_type_ids = bs_room_types.mapped("pms_room_type_id")

    @api.onchange("board_service_id", "pms_property_ids")
    def _onchange_filters(self):
        if not self.board_service_id:
            self.pms_property_ids = False
            self.room_type_ids = False
            return
        if self.pms_property_ids and self.available_property_ids:
            self.pms_property_ids = self.pms_property_ids & self.available_property_ids
        if self.room_type_ids and self.available_room_type_ids:
            self.room_type_ids = self.room_type_ids & self.available_room_type_ids

    @api.constrains("date_start", "date_end")
    def _check_date_range(self):
        for record in self:
            if record.date_start or record.date_end:
                if not record.date_start or not record.date_end:
                    raise ValidationError(_("Start Date and End Date are required."))
                if record.date_start > record.date_end:
                    raise ValidationError(_("Start Date must be before End Date."))

    @api.constrains(
        "weekday_monday",
        "weekday_tuesday",
        "weekday_wednesday",
        "weekday_thursday",
        "weekday_friday",
        "weekday_saturday",
        "weekday_sunday",
        "date_start",
        "date_end",
    )
    def _check_weekdays(self):
        for record in self:
            has_weekdays = any(
                [
                    record.weekday_monday,
                    record.weekday_tuesday,
                    record.weekday_wednesday,
                    record.weekday_thursday,
                    record.weekday_friday,
                    record.weekday_saturday,
                    record.weekday_sunday,
                ]
            )
            has_dates = bool(record.date_start and record.date_end)
            if not has_weekdays and not has_dates:
                raise ValidationError(
                    _("Select at least one weekday or define a date range.")
                )

    def action_create_rules(self):
        self.ensure_one()
        domain = [("pms_board_service_id", "=", self.board_service_id.id)]
        if self.room_type_ids:
            domain.append(("pms_room_type_id", "in", self.room_type_ids.ids))
        if self.pms_property_ids:
            domain.extend(
                [
                    "|",
                    ("pms_property_id", "=", False),
                    ("pms_property_id", "in", self.pms_property_ids.ids),
                ]
            )
        board_service_room_types = self.env["pms.board.service.room.type"].search(
            domain
        )
        if not board_service_room_types:
            raise UserError(
                _("No board service room types found with the selected filters.")
            )
        rule_model = self.env["pms.board.service.room.type.line.rule"]
        created = 0
        updated = 0
        for board_service_room_type in board_service_room_types:
            for line in board_service_room_type.board_service_line_ids:
                vals = {
                    "board_service_room_type_line_id": line.id,
                    "amount": self.amount,
                    "active": True,
                    "date_start": self.date_start,
                    "date_end": self.date_end,
                    "weekday_monday": self.weekday_monday,
                    "weekday_tuesday": self.weekday_tuesday,
                    "weekday_wednesday": self.weekday_wednesday,
                    "weekday_thursday": self.weekday_thursday,
                    "weekday_friday": self.weekday_friday,
                    "weekday_saturday": self.weekday_saturday,
                    "weekday_sunday": self.weekday_sunday,
                }
                rule_domain = [
                    ("board_service_room_type_line_id", "=", line.id),
                    ("date_start", "=", self.date_start),
                    ("date_end", "=", self.date_end),
                    ("weekday_monday", "=", self.weekday_monday),
                    ("weekday_tuesday", "=", self.weekday_tuesday),
                    ("weekday_wednesday", "=", self.weekday_wednesday),
                    ("weekday_thursday", "=", self.weekday_thursday),
                    ("weekday_friday", "=", self.weekday_friday),
                    ("weekday_saturday", "=", self.weekday_saturday),
                    ("weekday_sunday", "=", self.weekday_sunday),
                ]
                existing = rule_model.search(rule_domain, limit=1)
                if existing:
                    existing.write(vals)
                    updated += 1
                else:
                    rule_model.create(vals)
                    created += 1
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Board Service Rules"),
                "message": _("Rules created: %(created)s, updated: %(updated)s")
                % {"created": created, "updated": updated},
                "sticky": False,
            },
        }
