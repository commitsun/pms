# Copyright 2018-2021  Jose Luis Algara <osotranquilo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import _, fields, models


class InheritPmsReservation(models.Model):
    _inherit = "pms.reservation"

    door_codes = fields.Html("Entry Codes", compute="_compute_door_codes")
    box_number = fields.Integer("Box number")
    box_code = fields.Char("Box code")

    def doorcode4(self, date):
        # Calculate de Door Code...
        pms_property_id = self.pms_property_id
        if not pms_property_id.chararters_precode:
            pms_property_id.chararters_precode = ""
        if not pms_property_id.chararters_postcode:
            pms_property_id.chararters_postcode = ""
        delay = pms_property_id.seed_code * 100
        if pms_property_id.code_period == "7":
            weekday = date.weekday()  # Dias a restar para lunes
            date = date - timedelta(days=weekday)
        date = datetime(
            year=date.year,
            month=date.month,
            day=date.day,
        )
        code = float(date.strftime("%s.%%06d") % date.microsecond) + delay
        return (
            pms_property_id.chararters_precode
            + repr(code)[4:8]
            + pms_property_id.chararters_postcode
        )

    def door_codes_text(self, entry, exit):
        pms_property_id = self.pms_property_id
        codes = "No data"
        if pms_property_id.code_period == "7":
            if entry.weekday() == 0:
                entry = entry + timedelta(days=1)
            if exit.weekday() == 0:
                exit = exit - timedelta(days=1)
            codes = (
                _("Entry code: ")
                + '<strong><span style="font-size: 1.4em;">'
                + self.doorcode4(entry)
                + "</span></strong>"
            )
            while entry <= exit:
                if entry.weekday() == 0:
                    codes += (
                        "<br>"
                        + _("It will change on monday ")
                        + datetime.strftime(entry, "%d-%m-%Y")
                        + _(" to:")
                        + ' <strong><span style="font-size: 1.4em;">'
                        + self.doorcode4(entry)
                        + "</span></strong>"
                    )
                entry = entry + timedelta(days=1)
        else:
            codes = (
                _("Entry code: ")
                + '<strong><span style="font-size: 1.4em;">'
                + self.doorcode4(entry)
                + "</span></strong>"
            )
            entry = entry + timedelta(days=1)
            while entry < exit:
                codes += (
                    "<br>"
                    + _("It will change on ")
                    + datetime.strftime(entry, "%d-%m-%Y")
                    + _(" to:")
                    + ' <strong><span style="font-size: 1.4em;">'
                    + self.doorcode4(entry)
                    + "</span></strong>"
                )
                entry = entry + timedelta(days=1)
        return codes

    def _compute_door_codes(self):
        for record in self:
            record.door_codes = self.door_codes_text(record.checkin, record.checkout)
