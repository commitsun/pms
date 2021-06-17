##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2018-2021  Alda Hotels <informatica@aldahotels.com>
#                             Jose Luis Algara <osotranquilo@gmail.com>
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
from odoo import _, api, fields, models


class PmsProperty(models.Model):
    _inherit = "pms.property"

    chararters_precode = fields.Char(
        string="Characters before the door code", default=""
    )
    chararters_postcode = fields.Char(string="Characters after the code", default="")
    code_period = fields.Selection(
        [("7", "Change Monday"), ("1", "Change Diary")],
        help="Select a valid period type",
        string="Period of code change",
        default="7",
        required=True,
    )

    seed_code = fields.Integer(
        string="4 digit Seed Code", help="Must be between 0 and 9999", default=0
    )

    @api.constrains("seed_code")
    def _check_seed_code(self):
        for record in self.filtered("seed_code"):
            if record.seed_code > 9999:
                raise models.ValidationError(
                    _("The seed for the code must be between 0 and 9999")
                )
