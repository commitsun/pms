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

{
    "name": "PMS Hotel Door Codes",
    "version": "14.0.1.0.1",
    "author": "Jose Luis Algara Toledo <osotranquilo@gmail.com>,"
    "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "category": "pms hotel",
    "website": "https://github.com/OCA/pms",
    "depends": [
        "pms",
        "pms_l10n_es",
    ],
    "summary": "Generate Hotel door codes, in Pseudo random system",
    "data": [
        # 'wizard/door_code.xml',
        # 'data/menus.xml',
        # 'views/inherit_res_company.xml',
        "views/pms_reservation.xml",
        "views/pms_property_views.xml",
    ],
    "qweb": [],
    "test": [],
    "installable": True,
    "auto_install": False,
}
