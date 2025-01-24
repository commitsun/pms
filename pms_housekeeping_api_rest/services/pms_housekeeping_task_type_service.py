from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component

from ..pms_housekeeping_api_rest_utils import check_api_housekeeping_access

class PmsHousekeepingTaskType(Component):
    _inherit = "base.rest.service"
    _name = "pms.housekeeping.task.type"
    _usage = "task-types"
    _collection = "pms.housekeeping.services"

    @restapi.method(
        [
            (
                [
                    "/",
                ],
                "GET",
            )
        ],
        input_param=Datamodel("pms.housekeeping.task.type.input", is_list=False),
        output_param=Datamodel("pms.housekeeping.task.type.info", is_list=True),
        auth="jwt_api_pms_housekeeping",
    )
    def get_task_types(self, task_type_search):
        if check_api_housekeeping_access(self.env.user, task_type_search.pmsPropertyUuid):
            result_task_types = []
            domain = []
            if task_type_search.pmsPropertyUuid:
                pms_property = self.env["pms.property"].sudo().search(
                    [("housekeeping_uuid", "=", task_type_search.pmsPropertyUuid)]
                )
                domain += [
                    "|",
                    ("pms_property_ids", "in", [pms_property.id]),
                    ("pms_property_ids", "=", False),
                ]
            if task_type_search.employeeUuid:
                employee = self.env["hr.employee"].sudo().search(
                    [("housekeeping_uuid", "=", task_type_search.employeeUuid)]
                )
                domain += [
                    "|",
                    ("housekeeper_ids", "in", [employee.id]),
                    ("housekeeper_ids", "=", False),
                ]
            PmsHousekeepingTaskType = self.env.datamodels["pms.housekeeping.task.type.info"]

            for task_type in self.env["pms.housekeeping.task.type"].sudo().search(domain):
                result_task_types.append(
                    PmsHousekeepingTaskType(
                        uuid=task_type.housekeeping_uuid,
                        name=task_type.name,
                    )
                )
            return result_task_types

    @restapi.method(
        [
            (
                [
                    "/<string:task_type_uuid>",
                ],
                "GET",
            )
        ],
        input_param=Datamodel("pms.housekeeping.task.type.input", is_list=False),
        output_param=Datamodel("pms.housekeeping.task.type.info", is_list=False),
        auth="jwt_api_pms_housekeeping",
    )
    def get_task_type(self, task_type_uuid, task_type_search):
        if check_api_housekeeping_access(self.env.user, task_type_search.pmsPropertyUuid):
            task_type = self.env["pms.housekeeping.task.type"].sudo().search([("housekeeping_uuid", "=", task_type_uuid)])
            PmsHousekeepingTaskType = self.env.datamodels["pms.housekeeping.task.type.info"]
            return PmsHousekeepingTaskType(
                uuid=task_type.housekeeping_uuid,
                name=task_type.name,
            )
