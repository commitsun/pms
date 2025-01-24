from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel


class PmsHousekeepingTaskInput(Datamodel):
    _name = "pms.housekeeping.task.input"
    _inherit = "pms.housekeeping.rest.metadata"
    name = fields.String(required=False, allow_none=True)
    dateFrom = fields.String(required=False, allow_none=True)
    dateTo = fields.String(required=False, allow_none=True)
    date = fields.String(required=False, allow_none=True)
    completedDateTime = fields.String(required=False, allow_none=True)
    states = fields.List(fields.String(), required=False, allow_none=True)
    taskTypeUuid = fields.String(required=False, allow_none=True)
    roomUuid = fields.String(required=False, allow_none=True)
    employeeUuid = fields.String(required=False, allow_none=True)
    pmsPropertyUuid = fields.String(required=False, allow_none=True)


class PmsHousekeepingTaskInfo(Datamodel):
    _name = "pms.housekeeping.task.info"
    uuid = fields.String(required=False, allow_none=True)
    priority = fields.Integer(required=False, allow_none=True)
    name = fields.String(required=False, allow_none=True)
    pmsPropertyUuid = fields.String(required=False, allow_none=True)
    employeeUuid = fields.String(required=False, allow_none=True)
    taskTypeUuid = fields.String(required=False, allow_none=True)
    roomUuid = fields.String(required=False, allow_none=True)
    date = fields.String(required=False, allow_none=True)
    completedDateTime = fields.String(required=False, allow_none=True)
    state = fields.String(required=False, allow_none=True)
    description = fields.String(required=False, allow_none=True)
    label = fields.String(required=False, allow_none=True)
    annotations = fields.String(required=False, allow_none=True)
    tags = fields.String(required=False, allow_none=True)
    reservationUuid = fields.String(required=False, allow_none=True)


class PmsHousekeepingTaskResults(Datamodel):
    _name = "pms.housekeeping.task.results"
    total = fields.Integer(required=False, allow_none=True)
