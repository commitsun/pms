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

            result_partners.append(
                PmsPartnerInfo(
                    id=partner.id,
                    name=partner.name if partner.name else None,
                    firstname=partner.firstname if partner.firstname else None,
                    lastname=partner.lastname if partner.lastname else None,
                    lastname2=partner.lastname2 if partner.lastname2 else None,
                    email=partner.email if partner.email else None,
                    isAgency=partner.is_agency,
                    countryId=partner.residence_country_id.id
                    if partner.residence_country_id
                    else None,
                    countryChar=partner.residence_country_id.code_alpha3
                    if partner.residence_country_id
                    else None,
                    countryName=partner.residence_country_id.name
                    if partner.residence_country_id
                    else None,
                    tagIds=partner.category_id.ids if partner.category_id else [],
                )
            )
        return result_partners

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
