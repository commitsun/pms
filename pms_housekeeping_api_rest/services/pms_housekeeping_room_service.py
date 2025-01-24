from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component
from datetime import date, timedelta

from ..pms_housekeeping_api_rest_utils import check_api_housekeeping_access


class PmsHousekeepingPropertyService(Component):
    _inherit = "base.rest.service"
    _name = "pms.housekeeping.room.service"
    _usage = "rooms"
    _collection = "pms.housekeeping.services"

    @restapi.method(
        [
            (
                [
                    "/",
                ],
                "GET",
            )
        ],
        input_param=Datamodel("pms.housekeeping.room.input", is_list=False),
        output_param=Datamodel("pms.housekeeping.room.info", is_list=True),
        auth="jwt_api_pms_housekeeping",
    )
    def get_rooms(self, room_search):
        if check_api_housekeeping_access(self.env.user, room_search.pmsPropertyUuid):

            domain = []
            if room_search.pmsPropertyUuid:
                pms_property = self.env["pms.property"].sudo().search(
                    [("housekeeping_uuid", "=", room_search.pmsPropertyUuid)]
                )
                domain.append(("pms_property_id", "=", pms_property.id))
            result_rooms = []
            PmsRoomInfo = self.env.datamodels["pms.housekeeping.room.info"]
            for room in self.env["pms.room"].sudo().search(
                domain,
            ):
                num_days_empty = None
                previous_room_reservations = self.env["pms.reservation"].sudo().search(
                    [
                        ("checkout", "<", date.today()),
                        ("pms_property_id", "=", room.pms_property_id.id),
                    ]
                )
                checkouts = (
                    self.env["pms.reservation.line"]
                    .sudo()
                    .search(
                        [
                            ("reservation_id", "in", previous_room_reservations.ids),
                            ("room_id", "=", room.id),
                        ],
                    )
                    .mapped("date")
                )
                if checkouts:
                    last_checkout = max(checkouts)
                    days_between_last_checkout_and_today = (date.today()) - (
                        last_checkout + timedelta(days=1)
                    )
                    num_days_empty = days_between_last_checkout_and_today.days
                result_rooms.append(
                    PmsRoomInfo(
                        uuid=room.housekeeping_uuid,
                        name=room.name,
                        shortName=room.short_name,
                        numDaysEmpty=num_days_empty,
                    )
                )
            return result_rooms

    @restapi.method(
        [
            (
                [
                    "/<string:room_uuid>",
                ],
                "GET",
            )
        ],
        input_param=Datamodel("pms.housekeeping.room.input", is_list=False),
        output_param=Datamodel("pms.housekeeping.room.info", is_list=False),
        auth="jwt_api_pms_housekeeping",
    )
    def get_room(self, room_uuid, room_search):
        if check_api_housekeeping_access(self.env.user, room_search.pmsPropertyUuid):
            room = self.env["pms.room"].sudo().search([("housekeeping_uuid", "=", room_uuid)])
            PmsRoomInfo = self.env.datamodels["pms.housekeeping.room.info"]
            num_days_empty = None
            previous_room_reservations = self.env["pms.reservation"].sudo().search(
                [
                    ("checkout", "<", date.today()),
                    ("pms_property_id", "=", room.pms_property_id.id),
                ]
            )
            checkouts = (
                self.env["pms.reservation.line"]
                .sudo()
                .search(
                    [
                        ("reservation_id", "in", previous_room_reservations.ids),
                        ("room_id", "=", room.id),
                    ],
                )
                .mapped("date")
            )
            if checkouts:
                last_checkout = max(checkouts)
                days_between_last_checkout_and_today = (date.today()) - (
                    last_checkout + timedelta(days=1)
                )
                num_days_empty = days_between_last_checkout_and_today.days
            return PmsRoomInfo(
                uuid=room.housekeeping_uuid,
                name=room.name,
                shortName=room.short_name,
                numDaysEmpty=num_days_empty,
            )
