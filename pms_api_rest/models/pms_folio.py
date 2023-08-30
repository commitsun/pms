from werkzeug.exceptions import BadRequest

from odoo import models, _


class PmsFolio(models.Model):
    _inherit = "pms.folio"

    def build_reservations_cmds(self, folio_record, reservations):
        cmds = []
        existing_reservation_ids = []
        for reservation in reservations:
            reservation_vals = {}
            reservation_record = self.env["pms.reservation"].search([("id", "=", reservation.id)])
            if reservation_record:
                existing_reservation_ids.append(reservation_record.id)
            # checkin
            if reservation.checkin is not None:
                if (
                    reservation_record and reservation.checkin != str(reservation_record.checkin)
                    or not reservation_record
                ):
                    reservation_vals.update({"checkin": reservation.checkin})
            # checkout
            if reservation.checkout is not None:
                if (
                    reservation_record and reservation.checkout != str(reservation_record.checkout)
                    or not reservation_record
                ):
                    reservation_vals.update({"checkout": reservation.checkout})
            # roomTypeId
            if reservation.roomTypeId is not None:
                if (
                    reservation_record and reservation.roomTypeId != reservation_record.room_type_id.id
                    or not reservation_record
                ):
                    reservation_vals.update({"room_type_id": reservation.roomTypeId})
            # adults
            if reservation.adults is not None:
                if (
                    reservation_record and reservation.adults != reservation_record.adults
                    or not reservation_record
                ):
                    reservation_vals.update({"adults": reservation.adults})
            # children
            if reservation.children is not None:
                if (
                    reservation_record and reservation.children != reservation_record.children
                    or not reservation_record
                ):
                    reservation_vals.update({"children": reservation.children})

            # board_service_room_id
            if reservation.boardServiceId is not None:
                if (
                    reservation_record
                    and reservation.boardServiceId != reservation_record.board_service_room_id.id
                    or not reservation_record
                ):
                    reservation_vals.update(
                        {
                            "board_service_room_id": reservation.boardServiceId if (
                                reservation.boardServiceId != 0
                            ) else False
                        }
                    )

            # reservation_lines
            if reservation.reservationLines is not None:
                cmds_reservation_lines = self.env['pms.reservation'].build_reservation_lines_cmds(
                    reservation_record,
                    reservation.reservationLines
                )
                if cmds_reservation_lines:
                    reservation_vals.update(
                        {
                            "reservation_line_ids": cmds_reservation_lines
                        }
                    )
            # service_ids
            cmds_service_ids = self.env['pms.reservation'].build_reservation_services_cmds(
                reservation_record,
                reservation.services if reservation.services else [],
                reservation.boardServiceId if reservation.boardServiceId else False,
            )
            if cmds_service_ids:
                reservation_vals.update(
                    {
                        "service_ids": cmds_service_ids
                    }
                )
            if reservation_vals:
                if reservation_record:
                    cmds.append((1, reservation_record.id, reservation_vals))
                else:
                    cmds.append((0, 0, reservation_vals))
        # detect if the folio has reservations not in the request
        if folio_record.reservation_ids.filtered(
            lambda x: x.id not in existing_reservation_ids and x.state != 'cancel'
        ):
            raise BadRequest(_("Removing reservations is not allowed"))
        return cmds

    def build_creation_update_services_cmds(self, services):
        cmds = []
        existing_service_ids = []
        for service in services:
            service_record = self.env["pms.service"].search(
                [
                    ("id", "=", service.id)
                ]
            )
            if service_record:
                existing_service_ids.append(service_record.id)
            service_vals = {}
            # product_id
            if service.productId is not None:
                if (
                    service_record and service.productId != service_record.product_id.id
                    or not service_record
                ):
                    service_vals.update({"product_id": service.productId})
            # name
            if service.name is not None:
                if (
                    service_record and service.name != service_record.name
                    or not service_record
                ):
                    service_vals.update({"name": service.name})
            # isBoardService
            if service.isBoardService is not None:
                if (
                    service_record and service.isBoardService != service_record.is_board_service
                    or not service_record
                ):
                    service_vals.update({"is_board_service": service.isBoardService})
            # serviceLines
            if service.serviceLines is not None:
                cmds_service_lines = self.build_service_lines_cmds(
                    service_record,
                    service.serviceLines
                )
                if cmds_service_lines:
                    service_vals.update(
                        {
                            "service_line_ids": cmds_service_lines
                        }
                    )
                service_vals.update({"no_auto_add_lines": True})
            if service_vals:
                if service_record:
                    cmds.append((1, service_record.id, service_vals))
                else:
                    cmds.append((0, 0, service_vals))
        return cmds, existing_service_ids

    def build_services_cmds(self, folio_record, services):
        cmds, existing_service_ids = self.build_creation_update_services_cmds(services)
        for service_to_remove in folio_record.service_ids.filtered(
            lambda x: x.id not in existing_service_ids and not x.reservation_id
        ):
            cmds.append((2, service_to_remove.id))
        return cmds

    def build_service_lines_cmds(self, service, service_lines):
        cmds = []
        existing_service_line_ids = []
        for service_line in service_lines:
            service_line_record = False
            if service:
                service_line_record = self.env["pms.service.line"].search(
                    [
                        ("date", "=", service_line.date),
                        ("service_id", "=", service.id)
                    ]
                )
            if service_line_record:
                existing_service_line_ids.append(service_line_record.id)

            service_line_vals = {}
            # date
            if service_line.date is not None:
                if (
                    (service_line_record and service_line.date != str(service_line_record.date))
                    or not service_line_record
                ):
                    service_line_vals.update({"date": service_line.date})
            # priceUnit
            if service_line.priceUnit is not None:
                if (
                    (service_line_record
                     and round(service_line.priceUnit, 2) != round(service_line_record.price_unit, 2))
                    or not service_line_record
                ):
                    service_line_vals.update({"price_unit": service_line.priceUnit})
            # discount
            if service_line.discount is not None:
                if (
                    (service_line_record
                     and round(service_line.discount, 2) != round(service_line_record.discount, 2))
                    or not service_line_record
                ):
                    service_line_vals.update({"discount": service_line.discount})
            # quantity
            if service_line.quantity is not None:
                if (
                    (service_line_record and service_line.quantity != service_line_record.day_qty)
                    or not service_line_record
                ):
                    service_line_vals.update({"day_qty": service_line.quantity})
            if service_line_vals:
                if not service_line_record:
                    cmds.append((0, 0, service_line_vals))
                else:
                    cmds.append((1, service_line_record.id, service_line_vals))
        if service:
            for service_line_to_remove in service.service_line_ids.filtered(
                lambda x: x.id not in existing_service_line_ids
            ):
                cmds.append((2, service_line_to_remove.id))
        return cmds
