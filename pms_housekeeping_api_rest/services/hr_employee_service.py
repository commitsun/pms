from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component

from ..pms_housekeeping_api_rest_utils import url_image_pms_api_rest, check_api_housekeeping_access


class PmsHousekeepingEmployeeService(Component):
    _inherit = "base.rest.service"
    _name = "pms.housekeeping.employee.service"
    _usage = "employees"
    _collection = "pms.housekeeping.services"


    @restapi.method(
        [
            (
                [
                    "/<string:employee_uuid>",
                ],
                "GET",
            )
        ],
        input_param=Datamodel("hr.employee.input", is_list=False),
        output_param=Datamodel("hr.employee.output", is_list=False),
        auth="jwt_api_pms_housekeeping",
    )
    def get_employee(self, employee_uuid, employee_search):
        if check_api_housekeeping_access(self.env.user, employee_search.pmsPropertyUuid):
            employee = self.env["hr.employee"].sudo().search([("housekeeping_uuid", "=", employee_uuid)])
            return self.env.datamodels["hr.employee.output"](
                uuid=employee.housekeeping_uuid,
                name=employee.name,
                thumbnail=url_image_pms_api_rest("hr.employee", employee.id, "image_1920") if employee.image_1920 else None,
                email=employee.work_email if employee.work_email else None,
                phone=employee.work_phone if employee.work_phone else employee.mobile_phone if employee.mobile_phone else None,
                parentUuid=employee.parent_id.housekeeping_uuid if employee.parent_id else None,
            )
