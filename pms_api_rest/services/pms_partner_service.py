from datetime import datetime

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component


class PmsPartnerService(Component):
    _inherit = "base.rest.service"
    _name = "pms.partner.service"
    _usage = "partners"
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
        output_param=Datamodel("pms.partner.info", is_list=True),
        auth="jwt_api_pms",
    )
    def get_partners(self):
        result_partners = []
        PmsPartnerInfo = self.env.datamodels["pms.partner.info"]
        for partner in self.env["res.partner"].search([]):
            checkouts = (
                self.env["pms.checkin.partner"]
                .search([("partner_id.id", "=", partner.id)])
                .mapped("checkout")
            )
            result_partners.append(
                PmsPartnerInfo(
                    id=partner.id,
                    name=partner.name if partner.name else None,
                    firstname=partner.firstname if partner.firstname else None,
                    lastname=partner.lastname if partner.lastname else None,
                    lastname2=partner.lastname2 if partner.lastname2 else None,
                    email=partner.email if partner.email else None,
                    isAgency=partner.is_agency,
                    mobile=str(partner.mobile),
                    residenceStreet=partner.residence_street
                    if partner.residence_street
                    else None,
                    residenceStreet2=partner.residence_street2
                    if partner.residence_street2
                    else None,
                    residenceZip=partner.residence_zip
                    if partner.residence_zip
                    else None,
                    residenceCity=partner.residence_city
                    if partner.residence_city
                    else None,
                    countryId=partner.residence_country_id.id
                    if partner.residence_country_id
                    else None,
                    residenceStateId=partner.residence_state_id.id
                    if partner.residence_state_id
                    else None,
                    agencyStreet=partner.street if partner.street else None,
                    agencyStreet2=partner.street2 if partner.street2 else None,
                    agencyZip=partner.zip if partner.zip else None,
                    agencyCountryId=partner.country_id.id
                    if partner.country_id
                    else None,
                    agencyStateId=partner.state_id.id if partner.state_id else None,
                    agencyCity=partner.city if partner.city else None,
                    tagIds=partner.category_id.ids if partner.category_id else [],
                    lastStay=max(checkouts).strftime("%d/%m/%Y") if checkouts else "",
                    vatNumber=partner.vat if partner.vat else None,
                    vatDocumentType=partner.vat_document_type
                    if partner.vat_document_type
                    else None,
                )
            )
        return result_partners

    @restapi.method(
        [
            (
                [
                    "/<int:partner_id>/hosted-reservations",
                ],
                "GET",
            )
        ],
        output_param=Datamodel("pms.reservation.short.info", is_list=True),
        auth="jwt_api_pms",
    )
    def get_partner_as_host(self, partner_id):
        checkins = self.env["pms.checkin.partner"].search(
            [("partner_id", "=", partner_id)]
        )
        PmsReservationShortInfo = self.env.datamodels["pms.reservation.short.info"]
        reservations = []
        if checkins:
            for checkin in checkins:
                reservation = self.env["pms.reservation"].search(
                    [("id", "=", checkin.reservation_id.id)]
                )
                folio = self.env["pms.folio"].search(
                    [("id", "=", reservation.folio_id.id)]
                )
                reservations.append(
                    PmsReservationShortInfo(
                        id=reservation.id,
                        checkin=reservation.checkin.strftime("%d/%m/%Y"),
                        checkout=reservation.checkout.strftime("%d/%m/%Y"),
                        adults=reservation.adults,
                        priceTotal=round(reservation.price_room_services_set, 2),
                        stateDescription=dict(
                            reservation.fields_get(["state"])["state"]["selection"]
                        )[reservation.state],
                        paymentStateDescription=dict(
                            folio.fields_get(["payment_state"])["payment_state"][
                                "selection"
                            ]
                        )[folio.payment_state],
                    )
                )
            return reservations

    @restapi.method(
        [
            (
                [
                    "/<int:partner_id>/customer-reservations",
                ],
                "GET",
            )
        ],
        output_param=Datamodel("pms.reservation.short.info", is_list=True),
        auth="jwt_api_pms",
    )
    def get_partner_as_customer(self, partner_id):
        partnerReservations = self.env["pms.reservation"].search(
            [("partner_id", "=", partner_id)]
        )
        PmsReservationShortInfo = self.env.datamodels["pms.reservation.short.info"]
        reservations = []
        for reservation in partnerReservations:
            folio = self.env["pms.folio"].search([("id", "=", reservation.folio_id.id)])
            reservations.append(
                PmsReservationShortInfo(
                    checkin=datetime.combine(
                        reservation.checkin, datetime.min.time()
                    ).isoformat(),
                    checkout=datetime.combine(
                        reservation.checkout, datetime.min.time()
                    ).isoformat(),
                    adults=reservation.adults,
                    priceTotal=round(reservation.price_room_services_set, 2),
                    stateDescription=dict(
                        reservation.fields_get(["state"])["state"]["selection"]
                    )[reservation.state],
                    paymentStateDescription=dict(
                        folio.fields_get(["payment_state"])["payment_state"][
                            "selection"
                        ]
                    )[folio.payment_state],
                )
            )
            return reservations

    @restapi.method(
        [
            (
                [
                    "/<int:partner_id>/payments",
                ],
                "GET",
            )
        ],
        output_param=Datamodel("pms.payment.info", is_list=True),
        auth="jwt_api_pms",
    )
    def get_partner_payments(self, partner_id):
        partnerPayments = self.env["account.payment"].search(
            [("partner_id", "=", partner_id)]
        )
        PmsPaymentInfo = self.env.datamodels["pms.payment.info"]
        payments = []
        for payment in partnerPayments:
            payments.append(
                PmsPaymentInfo(
                    id=payment.id,
                    amount=round(payment.amount, 2),
                    journalId=payment.journal_id.id,
                    date=payment.date.strftime("%d/%m/%Y"),
                    memo=payment.ref,
                )
            )
        return payments

    @restapi.method(
        [
            (
                [
                    "/<int:partner_id>/invoices",
                ],
                "GET",
            )
        ],
        output_param=Datamodel("pms.account.move.info", is_list=True),
        auth="jwt_api_pms",
    )
    def get_partner_invoices(self, partner_id):
        partnerInvoices = self.env["account.move"].search(
            [("partner_id", "=", partner_id)]
        )
        PmsAcoountMoveInfo = self.env.datamodels["pms.account.move.info"]
        invoices = []
        for invoice in partnerInvoices:
            invoices.append(
                PmsAcoountMoveInfo(
                    id=invoice.id,
                    name=invoice.name,
                    amount=round(invoice.amount_total, 2),
                    date=invoice.date.strftime("%d/%m/%Y"),
                    state=invoice.state,
                    paymentState=invoice.payment_state
                    if invoice.payment_state
                    else None,
                )
            )
        return invoices

    @restapi.method(
        [
            (
                [
                    "/<string:documentType>/<string:documentNumber>",
                ],
                "GET",
            )
        ],
        output_param=Datamodel("pms.partner.info", is_list=True),
        auth="jwt_api_pms",
    )
    def get_partner_by_doc_number(self, document_type, document_number):
        doc_type = self.env["res.partner.id_category"].search(
            [("id", "=", document_type)]
        )
        doc_number = self.env["res.partner.id_number"].search(
            [("name", "=", document_number), ("category_id", "=", doc_type.id)]
        )
        partners = []
        PmsPartnerInfo = self.env.datamodels["pms.partner.info"]
        if not doc_number:
            pass
        else:
            if doc_number.valid_from:
                document_expedition_date = doc_number.valid_from.strftime("%d/%m/%Y")
            if doc_number.partner_id.birthdate_date:
                birthdate_date = doc_number.partner_id.birthdate_date.strftime(
                    "%d/%m/%Y"
                )
            partners.append(
                PmsPartnerInfo(
                    # id=doc_number.partner_id.id,
                    name=doc_number.partner_id.name
                    if doc_number.partner_id.name
                    else None,
                    firstname=doc_number.partner_id.firstname
                    if doc_number.partner_id.firstname
                    else None,
                    lastname=doc_number.partner_id.lastname
                    if doc_number.partner_id.lastname
                    else None,
                    lastname2=doc_number.partner_id.lastname2
                    if doc_number.partner_id.lastname2
                    else None,
                    email=doc_number.partner_id.email
                    if doc_number.partner_id.email
                    else None,
                    mobile=doc_number.partner_id.mobile
                    if doc_number.partner_id.mobile
                    else None,
                    documentType=doc_type.id,
                    documentNumber=doc_number.name,
                    documentExpeditionDate=document_expedition_date
                    if doc_number.valid_from
                    else None,
                    documentSupportNumber=doc_number.support_number
                    if doc_number.support_number
                    else None,
                    gender=doc_number.partner_id.gender
                    if doc_number.partner_id.gender
                    else None,
                    birthdate=birthdate_date
                    if doc_number.partner_id.birthdate_date
                    else None,
                    residenceStreet=doc_number.partner_id.residence_street
                    if doc_number.partner_id.residence_street
                    else None,
                    zip=doc_number.partner_id.residence_zip
                    if doc_number.partner_id.residence_zip
                    else None,
                    residenceCity=doc_number.partner_id.residence_city
                    if doc_number.partner_id.residence_city
                    else None,
                    nationality=doc_number.partner_id.nationality_id.id
                    if doc_number.partner_id.nationality_id
                    else None,
                    countryState=doc_number.partner_id.residence_state_id.id
                    if doc_number.partner_id.residence_state_id
                    else None,
                )
            )
        return partners
