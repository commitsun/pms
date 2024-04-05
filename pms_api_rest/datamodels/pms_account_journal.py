from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel


class PmsAccountJournalInfo(Datamodel):
    _name = "pms.account.journal.info"
    id = fields.Integer(required=True, allow_none=False)
    name = fields.String(required=True, allow_none=False)
    type = fields.String(required=True, allow_none=False)
    allowedPayments = fields.Boolean(required=True, allow_none=False)
