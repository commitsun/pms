from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel


class PmsAvailSearchParam(Datamodel):
    _name = "pms.avail.search.param"
    availabilityFrom = fields.String(required=True, allow_none=False)
    availabilityTo = fields.String(required=True, allow_none=False)
    pmsPropertyId = fields.Integer(required=True, allow_none=False)
    pricelistId = fields.Integer(required=False, allow_none=False)
    roomTypeId = fields.Integer(required=False, allow_none=False)
    realAvail = fields.Boolean(required=False, allow_none=False)
    currentLines = fields.List(fields.Integer(), required=False, allow_none=False)


class PmsAvailInfo(Datamodel):
    _name = "pms.avail.info"
    date = fields.String(required=True, allow_none=False)
    roomIds = fields.List(fields.Integer, required=True, allow_none=True)
