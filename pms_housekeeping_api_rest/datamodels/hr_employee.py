from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel


class HrEmployeeInput(Datamodel):
    _name = "hr.employee.input"
    pmsPropertyUuid = fields.String(required=False, allow_none=True)


class HrEmployeeOutput(Datamodel):
    _name = "hr.employee.output"
    uuid = fields.String(required=True, allow_none=False)
    name = fields.String(required=True, allow_none=False)
    thumbnail = fields.String(required=False, allow_none=True)
    email = fields.String(required=False, allow_none=True)
    phone = fields.String(required=False, allow_none=True)
    parentUuid = fields.String(required=False, allow_none=True)
