from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel


class PmsHousekeepingRoomInput(Datamodel):
    _name = "pms.housekeeping.room.input"
    userUuid = fields.String(required=False, allow_none=True)
    pmsPropertyUuid = fields.String(required=False, allow_none=True)


class PmsHousekeepingRoomInfo(Datamodel):
    _name = "pms.housekeeping.room.info"
    uuid = fields.String(required=False, allow_none=True)
    name = fields.String(required=False, allow_none=True)
    shortName = fields.String(required=False, allow_none=True)
    numDaysEmpty = fields.Integer(required=False, allow_none=True)
