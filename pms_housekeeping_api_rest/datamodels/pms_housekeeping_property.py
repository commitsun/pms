from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel


class PmsHousekeepingPropertyInfo(Datamodel):
    _name = "pms.housekeeping.property.info"
    uuid = fields.String(required=False, allow_none=True)
    name = fields.String(required=False, allow_none=True)
    stateName = fields.String(required=False, allow_none=True)
    hotelImageUrl = fields.String(required=False, allow_none=True)
    street = fields.String(required=False, allow_none=True)
    city = fields.String(required=False, allow_none=True)
    timezone = fields.String(required=False, allow_none=True)


class PmsHousekeepingPropertyInput(Datamodel):
    _name = "pms.housekeeping.property.input"
    employeeUuid = fields.String(required=False, allow_none=True)
