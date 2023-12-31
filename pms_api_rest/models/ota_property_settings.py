from odoo import fields, models


class OtaPropertySettings(models.Model):
    _name = "ota.property.settings"

    pms_property_id = fields.Many2one(
        string="PMS Property",
        help="PMS Property",
        comodel_name="pms.property",
        default=lambda self: self.env.user.get_active_property_ids()[0],
    )
    agency_id = fields.Many2one(
        string="Partner",
        help="Partner",
        comodel_name="res.partner",
        domain=[("is_agency", "=", True)],
    )
    pms_api_alowed_payments = fields.Boolean(
        string="PMS API Allowed Payments",
        help="PMS API Allowed Payments",
    )
    pms_api_payment_journal_id = fields.Many2one(
        string="Payment Journal",
        help="Payment Journal",
        comodel_name="account.journal",
    )
    pms_api_payment_identifier = fields.Char(
        string="Payment Identifier",
        help="""
            Text string used by the OTA to identify a prepaid reservation.
            The string will be searched within the partnerRequests parameter.
        """,
    )
