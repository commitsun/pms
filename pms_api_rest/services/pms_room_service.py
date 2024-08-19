from datetime import datetime

from odoo import _
from odoo.exceptions import MissingError
from odoo.odoo import fields

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component


class PmsRoomService(Component):
    _inherit = "base.rest.service"
    _name = "pms.room.service"
    _usage = "rooms"
    _collection = "pms.services"

    @restapi.method(
        [
            (
                [
                    "/",
                ],
                "GET",
            )
        ],
        input_param=Datamodel("pms.room.search.param"),
        output_param=Datamodel("pms.room.info", is_list=True),
        auth="jwt_api_pms",
    )
    def get_rooms(self, room_search_param):
        domain = []
        if room_search_param.name:
            domain.append(("name", "like", room_search_param.name))
        if room_search_param.pmsPropertyId:
            domain.append(("pms_property_id", "=", room_search_param.pmsPropertyId))
        if (
            room_search_param.availabilityFrom
            and room_search_param.availabilityTo
            and room_search_param.pmsPropertyId
        ):
            date_from = datetime.strptime(
                room_search_param.availabilityFrom, "%Y-%m-%d"
            ).date()
            date_to = datetime.strptime(
                room_search_param.availabilityTo, "%Y-%m-%d"
            ).date()
            pms_property = self.env["pms.property"].browse(
                room_search_param.pmsPropertyId
            )
            if not room_search_param.pricelistId:
                pms_property = self.env["pms.property"].browse(
                    room_search_param.pmsPropertyId
                )
                pms_property = pms_property.with_context(
                    checkin=date_from,
                    checkout=date_to,
                    room_type_id=False,  # Allows to choose any available room
                    current_lines=room_search_param.currentLines,
                    real_avail=True,
                )
            else:
                pms_property = pms_property.with_context(
                    checkin=date_from,
                    checkout=date_to,
                    room_type_id=False,  # Allows to choose any available room
                    current_lines=room_search_param.currentLines,
                    pricelist_id=room_search_param.pricelistId,
                    real_avail=True,
                )
            domain.append(("id", "in", pms_property.free_room_ids.ids))
        result_rooms = []
        PmsRoomInfo = self.env.datamodels["pms.room.info"]
        for room in (
            self.env["pms.room"]
            .search(
                domain,
            )
            .sorted("sequence")
        ):
            # TODO: avoid, change short_name,
            # set code amenities like a tag in room calendar name?
            short_name = room.short_name
            # if room.room_amenity_ids:
            #     for amenity in room.room_amenity_ids:
            #         if amenity.is_add_code_room_name:
            #             short_name += "%s" % amenity.default_code
            result_rooms.append(
                PmsRoomInfo(
                    id=room.id,
                    name=room.display_name,
                    roomTypeId=room.room_type_id,
                    capacity=room.capacity,
                    shortName=short_name,
                    roomTypeClassId=room.room_type_id.class_id,
                    ubicationId=room.ubication_id,
                    extraBedsAllowed=room.extra_beds_allowed,
                    roomAmenityIds=room.room_amenity_ids.ids
                    if room.room_amenity_ids
                    else None,
                    roomAmenityInName=room.room_amenity_ids.filtered(
                        lambda x: x.is_add_code_room_name
                    ).default_code
                    if room.room_amenity_ids.filtered(
                        lambda x: x.is_add_code_room_name
                    ).name
                    else "",
                    roomState=room.room_state,
                    outOfService=room.out_of_service,
                    outOfServiceReason=room.out_of_service_reason
                    if room.out_of_service_reason
                    else "",
                    outOfOrder=room.out_of_order,
                )
            )
        return result_rooms

    @restapi.method(
        [
            (
                [
                    "/<int:room_id>",
                ],
                "GET",
            )
        ],
        output_param=Datamodel("pms.room.info", is_list=False),
        auth="jwt_api_pms",
    )
    def get_room(self, room_id):
        room = self.env["pms.room"].search([("id", "=", room_id)])
        if room:
            PmsRoomInfo = self.env.datamodels["pms.room.info"]
            return PmsRoomInfo(
                id=room.id,
                name=room.name,
                roomTypeId=room.room_type_id,
                capacity=room.capacity,
                shortName=room.short_name,
                extraBedsAllowed=room.extra_beds_allowed,
            )
        else:
            raise MissingError(_("Room not found"))

    @restapi.method(
        [
            (
                [
                    "/<int:room_id>/reservations-out",
                ],
                "GET",
            )
        ],
        output_param=Datamodel("pms.reservation.short.info", is_list=False),
        auth="jwt_api_pms",
    )
    def get_reservations_out_by_room(self, room_id):
        reservation_out = self.env["pms.reservation"].search(
            [
                ("preferred_room_id", "=", room_id),
                ("reservation_type", "=", "out"),
                ("checkout", ">=", fields.Date.today()),
                ("checkin", "<=", fields.Date.today()),
            ]
        )
        if not reservation_out:
            reservation_out = self.env["pms.reservation"].search(
                [
                    ("preferred_room_id", "=", room_id),
                    ("reservation_type", "=", "out"),
                    ("checkin", ">", fields.Date.today()),
                ],
                limit=1,
                order="checkin asc",
            )
        PmsReservation = self.env.datamodels["pms.reservation.short.info"]
        if reservation_out:
            return PmsReservation(
                id=reservation_out.id,
                checkin=datetime.combine(
                    reservation_out.checkin, datetime.min.time()
                ).isoformat(),
                checkout=datetime.combine(
                    reservation_out.checkout, datetime.min.time()
                ).isoformat(),
                closureReasonId=reservation_out.closure_reason_id,
                outOfOrderDescription=reservation_out.out_order_description
                if reservation_out.out_order_description
                else "",
            )
        return PmsReservation()

    @restapi.method(
        [
            (
                [
                    "/p/<int:room_id>",
                ],
                "PATCH",
            )
        ],
        input_param=Datamodel("pms.room.info"),
        auth="jwt_api_pms",
    )
    def update_room(self, room_id, pms_room_info):
        room = self.env["pms.room"].search([("id", "=", room_id)])
        room_vals = {}
        if not room:
            raise MissingError(_("Room not found"))

        if pms_room_info.roomState:
            room_vals["room_state"] = pms_room_info.roomState
        if pms_room_info.outOfService:
            room_vals["out_of_service"] = pms_room_info.outOfService
        if pms_room_info.outOfServiceReason:
            room_vals["out_of_service_reason"] = pms_room_info.outOfServiceReason
        if pms_room_info.outOfOrder:
            room_vals["out_of_order"] = pms_room_info.outOfOrder

        if room_vals:
            room.write(room_vals)

    @restapi.method(
        [
            (
                [
                    "/<int:room_id>",
                ],
                "DELETE",
            )
        ],
        auth="jwt_api_pms",
    )
    def delete_room(self, room_id):
        # esto tb podría ser con un browse
        room = self.env["pms.room"].search([("id", "=", room_id)])
        if room:
            room.active = False
        else:
            raise MissingError(_("Room not found"))

    @restapi.method(
        [
            (
                [
                    "/",
                ],
                "POST",
            )
        ],
        input_param=Datamodel("pms.room.info"),
        auth="jwt_api_pms",
    )
    def create_room(self, pms_room_info_param):
        room = self.env["pms.room"].create(
            {
                "name": pms_room_info_param.name,
                "room_type_id": pms_room_info_param.roomTypeId,
                "capacity": pms_room_info_param.capacity,
                "short_name": pms_room_info_param.shortName,
            }
        )
        return room.id
