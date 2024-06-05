import logging

from odoo import api, fields, models

CODE_SPAIN = "ES"
CODE_NIF = "D"
CODE_NIE = "N"

_logger = logging.getLogger(__name__)


class PmsCheckinPartner(models.Model):
    _inherit = "pms.checkin.partner"

    support_number = fields.Char(
        string="Support number",
        help="ID support number",
        readonly=False,
        store=True,
        compute="_compute_support_number",
    )

    @api.depends("partner_id")
    def _compute_support_number(self):
        for record in self:
            if not record.support_number:
                if record.partner_id.id_numbers:
                    dni_numbers = record.partner_id.id_numbers.filtered(
                        lambda x: x.category_id.name == "DNI"
                    )
                    if len(dni_numbers) == 1 and dni_numbers.support_number:
                        record.support_number = dni_numbers.support_number
                    else:
                        record.support_number = False
                else:
                    record.support_number = False

    @api.model
    def _checkin_mandatory_fields(self, residence_country=False, document_type=False):
        mandatory_fields = super(PmsCheckinPartner, self)._checkin_mandatory_fields(
            residence_country, document_type
        )
        mandatory_fields.extend(
            [
                "birthdate_date",
                "gender",
                "document_number",
                "document_type",
                "document_expedition_date",
                "nationality_id",
                "residence_street",
                "residence_city",
                "residence_country_id",
                "residence_zip",
            ]
        )

        if residence_country and residence_country.code == CODE_SPAIN:
            mandatory_fields.extend(
                [
                    "residence_state_id",
                ]
            )
        if document_type.code and document_type.code == CODE_NIF:
            mandatory_fields.extend(
                [
                    "lastname2",
                ]
            )
        if document_type and document_type.code in [CODE_NIF, CODE_NIE]:
            mandatory_fields.extend(
                [
                    "support_number",
                ]
            )
        return mandatory_fields

    @api.model
    def _checkin_manual_fields(self, country=False):
        manual_fields = super(PmsCheckinPartner, self)._checkin_manual_fields()
        manual_fields.extend(["support_number"])
        return manual_fields
