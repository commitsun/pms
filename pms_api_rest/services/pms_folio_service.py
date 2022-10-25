from datetime import datetime, timedelta

from odoo import _, fields
from odoo.exceptions import MissingError
from odoo.osv import expression

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component


class PmsFolioService(Component):
    _inherit = "base.rest.service"
    _name = "pms.folio.service"
    _usage = "folios"
    _collection = "pms.services"

    @restapi.method(
        [
            (
                [
                    "/<int:folio_id>",
                ],
                "GET",
            )
        ],
        output_param=Datamodel("pms.folio.info", is_list=False),
        auth="jwt_api_pms",
    )
    def get_folio(self, folio_id):
        folio = self.env["pms.folio"].search(
            [
                ("id", "=", folio_id),
            ]
        )
        if folio:
            PmsFolioInfo = self.env.datamodels["pms.folio.info"]
            return PmsFolioInfo(
                id=folio.id,
                name=folio.name,
                partnerName=folio.partner_name if folio.partner_name else None,
                partnerPhone=folio.mobile if folio.mobile else None,
                partnerEmail=folio.email if folio.email else None,
                state=dict(folio.fields_get(["state"])["state"]["selection"])[
                    folio.state
                ],
                amountTotal=round(folio.amount_total, 2),
                reservationType=folio.reservation_type,
                pendingAmount=folio.pending_amount,
                lastCheckout=str(folio.last_checkout),
            )
        else:
            raise MissingError(_("Folio not found"))

    @restapi.method(
        [
            (
                [
                    "/",
                ],
                "GET",
            )
        ],
        input_param=Datamodel("pms.folio.search.param"),
        output_param=Datamodel("pms.folio.short.info", is_list=True),
        auth="jwt_api_pms",
    )
    def get_folios(self, folio_search_param):
        domain_fields = list()

        domain_fields.append(("pms_property_id", "=", folio_search_param.pmsPropertyId))

        if folio_search_param.dateTo and folio_search_param.dateFrom:
            date_from = fields.Date.from_string(folio_search_param.dateFrom)
            date_to = fields.Date.from_string(folio_search_param.dateTo)
            dates = [
                date_from + timedelta(days=x)
                for x in range(0, (date_to - date_from).days + 1)
            ]
            reservation_lines = list(
                set(
                    self.env["pms.reservation.line"]
                    .search([("date", "in", dates)])
                    .mapped("reservation_id")
                    .mapped("folio_id")
                    .ids
                )
            )
            domain_fields.append(("folio_id", "in", reservation_lines))

        domain_filter = list()
        if folio_search_param.filter:
            for search in folio_search_param.filter.split(" "):
                subdomains = [
                    [("name", "ilike", search)],
                    [("folio_id.name", "ilike", search)],
                    [("partner_name", "ilike", search)],
                    [("partner_id.firstname", "ilike", search)],
                    [("partner_id.lastname", "ilike", search)],
                    [("partner_id.id_numbers.name", "ilike", search)],
                ]
                domain_filter.append(expression.OR(subdomains))
        domain = []
        if domain_filter:
            domain = expression.AND([domain_fields, domain_filter[0]])
        else:
            domain = domain_fields
        result_folios = []

        reservations_result = (
            self.env["pms.reservation"].search(domain).mapped("folio_id").ids
        )

        PmsFolioShortInfo = self.env.datamodels["pms.folio.short.info"]
        for folio in self.env["pms.folio"].search(
            [("id", "in", reservations_result)],
        ):
            reservations = []
            for reservation in folio.reservation_ids:
                reservations.append(
                    {
                        "id": reservation.id,
                        "checkin": datetime.combine(
                            reservation.checkin, datetime.min.time()
                        ).isoformat(),
                        "checkout": datetime.combine(
                            reservation.checkout, datetime.min.time()
                        ).isoformat(),
                        "preferredRoomId": reservation.preferred_room_id.id
                        if reservation.preferred_room_id
                        else None,
                        "roomTypeId": reservation.room_type_id.id
                        if reservation.room_type_id
                        else None,
                        "adults": reservation.adults,
                        "pricelistId": reservation.pricelist_id.id
                        if reservation.pricelist_id
                        else None,
                        "saleChannelId": reservation.sale_channel_origin_id.id
                        if reservation.sale_channel_origin_id
                        else None,
                        "agencyId": reservation.agency_id.id
                        if reservation.agency_id
                        else None,
                        "splitted": reservation.splitted,
                    }
                )
            result_folios.append(
                PmsFolioShortInfo(
                    id=folio.id,
                    partnerName=folio.partner_name if folio.partner_name else None,
                    partnerPhone=folio.mobile if folio.mobile else None,
                    partnerEmail=folio.email if folio.email else None,
                    amountTotal=round(folio.amount_total, 2),
                    reservations=[] if not reservations else reservations,
                    paymentStateCode=folio.payment_state,
                    paymentStateDescription=dict(
                        folio.fields_get(["payment_state"])["payment_state"][
                            "selection"
                        ]
                    )[folio.payment_state],
                )
            )
        return result_folios

    @restapi.method(
        [
            (
                [
                    "/<int:folio_id>/payments",
                ],
                "GET",
            )
        ],
        input_param=Datamodel("pms.search.param"),
        output_param=Datamodel("pms.payment.info", is_list=True),
        auth="jwt_api_pms",
    )
    def get_folio_payments(self, folio_id, pms_search_param):
        domain = list()
        domain.append(("id", "=", folio_id))
        if pms_search_param.pmsPropertyId:
            domain.append(("pms_property_id", "=", pms_search_param.pmsPropertyId))
        folio = self.env["pms.folio"].search(domain)
        payments = []
        PmsPaymentInfo = self.env.datamodels["pms.payment.info"]
        if not folio:
            pass
        else:
            # if folio.payment_state == "not_paid":
            #     pass
            # else:
            if folio.payment_ids:
                for payment in folio.payment_ids:
                    payments.append(
                        PmsPaymentInfo(
                            id=payment.id,
                            amount=round(payment.amount, 2),
                            journalId=payment.journal_id.id,
                            date=datetime.combine(
                                payment.date, datetime.min.time()
                            ).isoformat(),
                            paymentType=payment.payment_type,
                        )
                    )
        return payments

    @restapi.method(
        [
            (
                [
                    "/<int:folio_id>/charge",
                ],
                "POST",
            )
        ],
        input_param=Datamodel("pms.account.payment.short.info", is_list=False),
        auth="jwt_api_pms",
    )
    def create_folio_charge(self, folio_id, pms_account_payment_info):
        folio = self.env["pms.folio"].browse(folio_id)
        partner_id = self.env["res.partner"].browse(pms_account_payment_info.partnerId)
        journal_id = self.env["account.journal"].browse(
            pms_account_payment_info.journalId
        )
        self.env["pms.folio"].do_payment(
            journal_id,
            journal_id.suspense_account_id,
            self.env.user,
            pms_account_payment_info.amount,
            folio,
            reservations=pms_account_payment_info.reservationIds,
            services=False,
            partner=partner_id,
            date=datetime.strptime(pms_account_payment_info.date, "%m/%d/%Y"),
        )

    @restapi.method(
        [
            (
                [
                    "/<int:folio_id>/refund",
                ],
                "POST",
            )
        ],
        input_param=Datamodel("pms.account.payment.short.info", is_list=False),
        auth="jwt_api_pms",
    )
    def create_folio_refund(self, folio_id, pms_account_payment_info):
        folio = self.env["pms.folio"].browse(folio_id)
        partner_id = self.env["res.partner"].browse(pms_account_payment_info.partnerId)
        journal_id = self.env["account.journal"].browse(
            pms_account_payment_info.journalId
        )
        self.env["pms.folio"].do_refund(
            journal_id,
            journal_id.suspense_account_id,
            self.env.user,
            pms_account_payment_info.amount,
            folio,
            reservations=False,
            services=False,
            partner=partner_id,
            date=datetime.strptime(pms_account_payment_info.date, "%m/%d/%Y"),
            ref=pms_account_payment_info.reference,
        )

    @restapi.method(
        [
            (
                [
                    "/<int:folio_id>/reservations",
                ],
                "GET",
            )
        ],
        output_param=Datamodel("pms.reservation.short.info", is_list=True),
        auth="jwt_api_pms",
    )
    def get_folio_reservations(self, folio_id):
        folio = self.env["pms.folio"].browse(folio_id)
        reservations = []
        PmsReservationShortInfo = self.env.datamodels["pms.reservation.short.info"]
        if not folio:
            pass
        else:
            if folio.reservation_ids:
                for reservation in folio.reservation_ids:
                    reservations.append(
                        PmsReservationShortInfo(
                            id=reservation.id,
                            boardServiceId=reservation.board_service_room_id.id
                            if reservation.board_service_room_id
                            else None,
                            checkin=datetime.combine(
                                reservation.checkin, datetime.min.time()
                            ).isoformat(),
                            checkout=datetime.combine(
                                reservation.checkout, datetime.min.time()
                            ).isoformat(),
                            roomTypeId=reservation.room_type_id.id
                            if reservation.room_type_id
                            else None,
                            preferredRoomId=reservation.preferred_room_id.id
                            if reservation.preferred_room_id
                            else None,
                            adults=reservation.adults,
                            stateCode=reservation.state,
                            stateDescription=dict(
                                reservation.fields_get(["state"])["state"]["selection"]
                            )[reservation.state],
                            children=reservation.children
                            if reservation.children
                            else None,
                            readyForCheckin=reservation.ready_for_checkin,
                            allowedCheckout=reservation.allowed_checkout,
                            splitted=reservation.splitted,
                            priceTotal=round(reservation.price_room_services_set, 2),
                            servicesCount=sum(
                                reservation.service_ids.filtered(
                                    lambda x: not x.is_board_service
                                ).mapped("product_qty")
                            ),
                        )
                    )

        return reservations

    @restapi.method(
        [
            (
                [
                    "/",
                ],
                "POST",
            )
        ],
        input_param=Datamodel("pms.folio.info", is_list=False),
        auth="jwt_api_pms",
    )
    def create_folio(self, pms_folio_info):
        if pms_folio_info.reservationType == "out":
            vals = {
                "pms_property_id": pms_folio_info.pmsPropertyId,
                "reservation_type": pms_folio_info.reservationType,
                "closure_reason_id": pms_folio_info.closureReasonId,
            }
        else:
            vals = {
                "pms_property_id": pms_folio_info.pmsPropertyId,
                "partner_id": pms_folio_info.partnerId,
                "sale_channel_origin_id": pms_folio_info.saleChannelId,
                "agency_id": pms_folio_info.agency,
                "reservation_type": pms_folio_info.reservationType,
            }
        folio = self.env["pms.folio"].create(vals)
        for reservation in pms_folio_info.reservations:
            vals = {
                "folio_id": folio.id,
                "room_type_id": reservation.roomTypeId,
                "checkin": reservation.checkin,
                "checkout": reservation.checkout,
                "pms_property_id": pms_folio_info.pmsPropertyId,
                "pricelist_id": pms_folio_info.pricelistId,
                "external_reference": pms_folio_info.externalReference,
                "board_service_room_id": reservation.boardServiceId,
                "preferred_room_id": reservation.preferredRoomId,
                "adults": reservation.adults,
                "reservation_type": pms_folio_info.reservationType,
                "children": reservation.children,
                "preconfirm": pms_folio_info.preconfirm,
            }
            reservation_record = self.env["pms.reservation"].create(vals)
            if reservation.services:
                for service in reservation.services:
                    vals = {
                        "product_id": service.productId,
                        "reservation_id": reservation_record.id,
                        "is_board_service": False,
                        "service_line_ids": [
                            (
                                0,
                                False,
                                {
                                    "date": line.date,
                                    "price_unit": line.priceUnit,
                                    "discount": line.discount or 0,
                                    "day_qty": line.quantity,
                                },
                            )
                            for line in service.serviceLines
                        ],
                    }
                    self.env["pms.service"].create(vals)

        return folio.id
