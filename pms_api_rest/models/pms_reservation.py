from odoo import fields, models


class PmsReservation(models.Model):
    _inherit = "pms.reservation"

    def build_reservation_lines_cmds(self, reservation, reservation_lines):
        cmds = []
        existing_reservation_line_ids = []
        for reservation_line in reservation_lines:
            reservation_line_vals = {}
            # search reservation line record
            reservation_line_record = self.env["pms.reservation.line"].search(
                [
                    ("date", "=", reservation_line.date),
                    ("reservation_id", "=", reservation.id)
                ]
            )
            if reservation_line_record:
                existing_reservation_line_ids.append(reservation_line_record.id)
            # only update reservation line vals if their fields are different than the record
            # date
            if reservation_line.date is not None:
                if (
                    (reservation_line_record and reservation_line.date != str(reservation_line_record.date))
                    or not reservation_line_record
                ):
                    reservation_line_vals.update({"date": reservation_line.date})
            # price
            if reservation_line.price is not None:
                if (
                    (
                        reservation_line_record
                        and round(reservation_line.price, 2) != round(reservation_line_record.price, 2)
                    )
                    or not reservation_line_record
                ):
                    reservation_line_vals.update({"price": reservation_line.price})
            # discount
            if reservation_line.discount is not None:
                if (
                    (
                        reservation_line_record
                        and round(reservation_line.discount, 2) != round(reservation_line_record.discount, 2))
                    or not reservation_line_record
                ):
                    reservation_line_vals.update({"discount": reservation_line.discount})
            # roomId
            if reservation_line.roomId is not None:
                if (
                    (reservation_line_record and reservation_line.roomId != reservation_line_record.room_id.id)
                    or not reservation_line_record
                ):
                    reservation_line_vals.update({"room_id": reservation_line.roomId})

            if reservation_line_vals:
                if not reservation_line_record:
                    cmds.append((0, 0, reservation_line_vals))
                else:
                    cmds.append((1, reservation_line_record.id, reservation_line_vals))

        for reservation_line_to_remove in reservation.reservation_line_ids.filtered(
            lambda x: x.id not in existing_reservation_line_ids
        ):
            cmds.append((2, reservation_line_to_remove.id))
        return cmds

    def build_reservation_services_cmds(self, reservation_record, services, board_service_id):
        cmds, existing_service_ids = self.env['pms.folio'].build_services_cmds(services)
        # remove board services if board_service_id is 0
        if board_service_id == 0:
            for board_service_to_remove in reservation_record.service_ids.filtered(lambda x: x.is_board_service):
                cmds.append((2, board_service_to_remove.id))
        # remove old services
        for service_to_remove in reservation_record.service_ids.filtered(lambda x: x.id not in existing_service_ids):
            cmds.append((2, service_to_remove.id))
        return cmds
