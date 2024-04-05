from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel


class PmsAccountTransactiontTermInfo(Datamodel):
    _name = "pms.account.transaction.term.info"
    id = fields.Integer(required=True, allow_none=False)
    name = fields.String(required=True, allow_none=False)
