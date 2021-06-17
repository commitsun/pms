##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2018-2021 Jose Luis Algara Toledo <osotranquilo@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import fields, models


class DoorCodeWizard(models.TransientModel):
    _name = "door_code"
    _description = "Check the door codes"
    _check_pms_properties_auto = True

    pms_property_ids = fields.Many2many(
        string="Properties",
        help="Properties with access to the element;"
        " if not set, all properties can access",
        required=True,
        comodel_name="pms.property",
        check_pms_properties=True,
    )

    date_start = fields.Date(
        "Start of the period", default=lambda self: fields.Datetime.now(), required=True
    )
    date_end = fields.Date(
        "End of period", default=lambda self: fields.Datetime.now(), required=True
    )
    door_code = fields.Html("Door codes")

    def check_code(self):
        reservation = self.env["pms.reservation"]
        codes = ""
        for property_id in self.pms_property_ids:
            codes += (
                '<br><strong><span style="font-size: 1.4em;">'
                + property_id.name
                + "</span></strong><br>"
            )
            reservation.pms_property_id = property_id
            codes += reservation.door_codes_text(
                self.date_start, self.date_end, property_id
            )
        return self.write({"door_code": codes})
