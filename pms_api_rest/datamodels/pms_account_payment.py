from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel


class PmsPaymentInfo(Datamodel):
    _name = "pms.payment.info"
    id = fields.Integer(required=False, allow_none=True)
    amount = fields.Float(required=False, allow_none=True)
    journalId = fields.Integer(required=False, allow_none=True)
    date = fields.String(required=False, allow_none=True)


class PmsAccountPaymentInfo(Datamodel):
    _name = "pms.account.payment.short.info"
    id = fields.Integer(required=False, allow_none=True)
    date = fields.String(required=False, allow_none=True)
    journalId = fields.Integer(required=False, allow_none=True)
    amount = fields.Float(required=False, allow_none=True)
    partnerName = fields.String(required=False, allow_none=True)
