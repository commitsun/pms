from odoo import api, fields, models


class PmsReservation(models.Model):
    _inherit = "pms.reservation"
    ses_comunication_ids = fields.One2many(
        string="SES Comunications",
        help="Comunications related to this reservation",
        comodel_name="pms.ses.comunication",
        inverse_name="reservation_id",
    )
    is_ses = fields.Boolean(
        string="Is SES",
        readonly=True,
        compute="_compute_is_ses",
    )

    @api.depends("pms_property_id")
    def _compute_is_ses(self):
        for record in self:
            record.is_ses = record.pms_property_id.institution == "ses"

    @api.model
    def create_comunication(self, reservation_id, operation, entity):
        self.env["pms.ses.comunication"].create(
            {
                "reservation_id": reservation_id,
                "operation": operation,
                "entity": entity,
            }
        )

    @api.model
    def create(self, vals):
        reservation = super(PmsReservation, self).create(vals)
        if reservation.pms_property_id.institution == "ses":
            self.create_comunication(reservation.id, "A", "RH")
        return reservation

    def write(self, vals):
        for record in self:
            if record.pms_property_id.institution == "ses":
                state_changed = "state" in vals and (
                    (vals["state"] != "cancel" and record.state == "cancel")
                    or (vals["state"] == "cancel" and record.state != "cancel")
                )
                check_changed = (
                    any(
                        key in vals and vals[key] != getattr(record, key)
                        for key in ["adults", "checkin", "checkout"]
                    )
                    and record.state != "cancel"
                )

                if state_changed or check_changed:
                    # delete all pending notifications
                    self.env["pms.ses.comunication"].search(
                        [
                            ("reservation_id", "=", record.id),
                            ("state", "=", "to_send"),
                            ("entity", "=", "RH"),
                        ]
                    ).unlink()

                    # last communication
                    last_comunication = self.env["pms.ses.comunication"].search(
                        [
                            ("reservation_id", "=", record.id),
                            ("entity", "=", "RH"),
                        ],
                        order="id desc",
                        limit=1,
                    )

                    if state_changed:
                        if (
                            vals["state"] == "cancel"
                            and last_comunication.operation == "A"
                        ):
                            self.create_comunication(record.id, "B", "RH")
                        elif (
                            vals["state"] != "cancel"
                            and last_comunication.operation == "B"
                        ):
                            self.create_comunication(record.id, "A", "RH")
                    elif check_changed:
                        if last_comunication.operation == "A":
                            self.create_comunication(record.id, "B", "RH")
                        self.create_comunication(record.id, "A", "RH")

        return super(PmsReservation, self).write(vals)

    def create_notifications_traveller_report_and_send(self, test=False):
        for record in self:
            if (
                record.pms_property_id.institution == "ses"
                and record.state == "onboard"
                and record.checkin == fields.Datetime.today().date()
                and any(
                    state == "onboard"
                    for state in record.checkin_partner_ids.mapped("state")
                )
            ):
                self.create_comunication(
                    record.id,
                    "A",
                    "PV",
                )
