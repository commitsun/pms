from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel


class PmsHousekeepingUserInput(Datamodel):
    _name = "pms.housekeeping.user.input"
    username = fields.String(required=False, allow_none=True)
    password = fields.String(required=False, allow_none=True)


class PmsHousekeepingUserOutput(Datamodel):
    _name = "pms.housekeeping.user.output"
    uuid = fields.String(required=True, allow_none=False)
    token = fields.String(required=False, allow_none=True)
    expirationDate = fields.Integer(required=False, allow_none=True)
    defaultPropertyUuid = fields.String(required=False, allow_none=True)
    employeeUuid = fields.String(required=False, allow_none=True)
