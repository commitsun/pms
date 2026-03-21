# Copyright 2026  Dario Lodeiros
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PmsBoardServiceRoomTypeLineRule(models.Model):
    _name = "pms.board.service.room.type.line.rule"
    _description = "Board Service Room Type Line Rule"
    _check_pms_properties_auto = True
    _order = "priority desc, id desc"

    active = fields.Boolean(default=True)
    priority = fields.Integer(
        default=lambda self: self._default_priority(),
        help="Higher value means higher priority.",
    )

    board_service_room_type_line_id = fields.Many2one(
        string="Board Service Line",
        comodel_name="pms.board.service.room.type.line",
        required=True,
        index=True,
        ondelete="cascade",
        check_pms_properties=True,
    )
    board_service_room_type_id = fields.Many2one(
        string="Board Service Room Type",
        related="board_service_room_type_line_id.pms_board_service_room_type_id",
        store=True,
    )
    pms_board_service_id = fields.Many2one(
        string="Board Service",
        related="board_service_room_type_id.pms_board_service_id",
        store=True,
    )
    pms_property_id = fields.Many2one(
        string="Property",
        related="board_service_room_type_id.pms_property_id",
        store=True,
    )
    pms_room_type_id = fields.Many2one(
        string="Room Type",
        related="board_service_room_type_id.pms_room_type_id",
        store=True,
    )
    pricelist_ids = fields.Many2many(
        string="Pricelists",
        comodel_name="product.pricelist",
        compute="_compute_pricelist_ids",
        store=True,
        readonly=True,
        relation="pms_bsrt_line_rule_pricelist_rel",
        column1="rule_id",
        column2="pricelist_id",
    )
    product_id = fields.Many2one(
        string="Product",
        related="board_service_room_type_line_id.product_id",
        store=True,
    )

    amount = fields.Float(
        string="Rule Price",
        required=True,
        digits=("Product Price"),
    )

    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")

    weekday_monday = fields.Boolean(string="Monday")
    weekday_tuesday = fields.Boolean(string="Tuesday")
    weekday_wednesday = fields.Boolean(string="Wednesday")
    weekday_thursday = fields.Boolean(string="Thursday")
    weekday_friday = fields.Boolean(string="Friday")
    weekday_saturday = fields.Boolean(string="Saturday")
    weekday_sunday = fields.Boolean(string="Sunday")

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

    @api.depends("board_service_room_type_id.pricelist_ids")
    def _compute_pricelist_ids(self):
        for record in self:
            record.pricelist_ids = record.board_service_room_type_id.pricelist_ids

    @api.model
    def _default_priority(self):
        return int(fields.Datetime.now().timestamp())

    def _is_applicable(self, date_value):
        self.ensure_one()
        if not date_value:
            return False
        date_ok = True
        if self.date_start and self.date_end:
            date_ok = self.date_start <= date_value <= self.date_end
        weekday_ok = True
        if any(
            [
                self.weekday_monday,
                self.weekday_tuesday,
                self.weekday_wednesday,
                self.weekday_thursday,
                self.weekday_friday,
                self.weekday_saturday,
                self.weekday_sunday,
            ]
        ):
            weekday = date_value.weekday()
            weekday_ok = [
                self.weekday_monday,
                self.weekday_tuesday,
                self.weekday_wednesday,
                self.weekday_thursday,
                self.weekday_friday,
                self.weekday_saturday,
                self.weekday_sunday,
            ][weekday]
        return date_ok and weekday_ok

    @api.model
    def get_applicable_rule(self, board_service_line, consumption_date):
        if not board_service_line or not consumption_date:
            return False
        date_value = fields.Date.to_date(consumption_date)
        if not date_value:
            return False
        rules = self.search(
            [
                ("active", "=", True),
                ("board_service_room_type_line_id", "=", board_service_line.id),
            ],
            order=self._order,
        )
        for rule in rules:
            if rule._is_applicable(date_value):
                return rule
        return False
