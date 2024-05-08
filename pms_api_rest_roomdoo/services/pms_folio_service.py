import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class PmsFolioService(Component):
    _inherit = "pms.folio.service"

    def _get_reservation_vals(self, folio, reservation, preconfirm):
        vals = super(PmsFolioService, self)._get_reservation_vals(
            self, folio, reservation, preconfirm
        )
        vals["blocked"] = True if self.env.user.pms_api_client else False
        return vals

    def _create_reservation_record(self, vals):
        self.env["pms.reservation"].with_context(
            skip_compute_service_ids=False if self.env.user.pms_api_client else True,
            force_overbooking=True if self.env.user.pms_api_client else False,
            force_write_blocked=True if self.env.user.pms_api_client else False,
        ).create(vals)

    def _force_compute_board_service_default(self, reservation_record):
        reservation_record.with_context(
            skip_compute_service_ids=False,
            force_write_blocked=True if self.env.user.pms_api_client else False,
        )._compute_board_service_room_id()

    def _insert_log_folio_creation(
        self,
        pms_property_id,
        log_payload,
        response,
        status,
        folio_ids,
        min_checkin_payload,
        max_checkout_payload,
    ):
        if self.env.user.pms_api_client:
            super(PmsFolioService, self)._insert_log_folio_creation(
                pms_property_id,
                log_payload,
                response,
                status,
                folio_ids,
                min_checkin_payload,
                max_checkout_payload,
            )

    def get_channel_origin_id(self, sale_channel_id, agency_id):
        """
        Returns the channel origin id for the given agency
        or website channel if not agency is given
        (TODO change by configuration user api in the future)
        """
        external_app = self.env.user.pms_api_client
        if sale_channel_id:
            return sale_channel_id
        if not agency_id and external_app:
            # TODO change by configuration user api in the future
            return (
                self.env["pms.sale.channel"]
                .search(
                    [("channel_type", "=", "direct"), ("is_on_line", "=", True)],
                    limit=1,
                )
                .id
            )
        agency = self.env["res.partner"].browse(agency_id)
        if agency:
            return agency.sale_channel_id.id
        return False

    def get_language(self, lang_code):
        """
        Returns the language for the given language code
        """
        external_app = self.env.user.pms_api_client
        if not external_app:
            return lang_code
        return self.env["res.lang"].search([("iso_code", "=", lang_code)], limit=1).code

    def get_board_service_room_type_id(
        self, board_service_id, room_type_id, pms_property_id
    ):
        """
        The internal app uses the board service room type id to create the reservation,
        but the external app uses the board service id and the room type id.
        Returns the board service room type id for the given board service and room type
        """
        board_service = self.env["pms.board.service"].browse(board_service_id)
        room_type = self.env["pms.room.type"].browse(room_type_id)
        external_app = self.env.user.pms_api_client
        if not external_app:
            return board_service_id
        if board_service and room_type:
            return (
                self.env["pms.board.service.room.type"]
                .search(
                    [
                        ("pms_board_service_id", "=", board_service.id),
                        ("pms_room_type_id", "=", room_type.id),
                        ("pms_property_id", "=", pms_property_id),
                    ],
                    limit=1,
                )
                .id
            )
        return False
