from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel


class PmsHousekeepingTaskTypeInput(Datamodel):
    _name = "pms.housekeeping.task.type.input"
    employeeUuid = fields.String(required=False, allow_none=True)
    pmsPropertyUuid = fields.String(required=False, allow_none=True)


class PmsHousekeepingTaskTypeInfo(Datamodel):
    _name = "pms.housekeeping.task.type.info"
    uuid = fields.String(required=False, allow_none=True)
    name = fields.String(required=False, allow_none=True)
