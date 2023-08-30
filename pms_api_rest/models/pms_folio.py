from odoo import fields, models


class PmsReservation(models.Model):
    _inherit = "pms.reservation"

    def build_reservation_or_folio_services_cmds(self, reservation_or_folio_record, services, from_folio=False):
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
        for service_to_remove in reservation_or_folio_record.service_ids.filtered(
            lambda x: x.id not in existing_service_ids and (
                (
                    (
                        from_folio and not x.reservation_id
                    )
                    or not from_folio
                )
            )
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
