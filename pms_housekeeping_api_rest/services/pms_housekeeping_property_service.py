from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component

from ..pms_housekeeping_api_rest_utils import url_image_pms_api_rest, check_api_housekeeping_access


class PmsHousekeepingPropertyService(Component):
    _inherit = "base.rest.service"
    _name = "pms.housekeeping.property.service"
    _usage = "properties"
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
        output_param=Datamodel("pms.housekeeping.property.info", is_list=True),
        input_param=Datamodel("pms.housekeeping.property.input"),
        auth="jwt_api_pms_housekeeping",
    )
    def get_properties(self, pms_housekeeping_property_input_param):
        result_properties = []
        PmsPropertyInfo = self.env.datamodels["pms.housekeeping.property.info"]

        employee = self.env["hr.employee"].sudo().search([("housekeeping_uuid", "=", pms_housekeeping_property_input_param.employeeUuid)])
        if employee and employee.property_ids:
            pms_properties_sudo = employee.property_ids
        else:
            pms_properties_sudo = self.env["pms.property"].sudo().search([])

        for pms_property in pms_properties_sudo:
            result_properties.append(
                PmsPropertyInfo(
                    uuid=pms_property.housekeeping_uuid,
                    name=pms_property.name,
                    hotelImageUrl=url_image_pms_api_rest(
                        "pms.property", pms_property.id, "hotel_image_pms_api_rest"
                    ),
                    city=pms_property.city if pms_property.city else None,
                    stateName=(
                        self.env["res.country.state"]
                        .search([("id", "=", pms_property.state_id.id)])
                        .name
                        if pms_property.state_id
                        else None
                    ),
                    timezone=pms_property.tz if pms_property.tz else None,
                )
            )
        return result_properties

    @restapi.method(
        [
            (
                [
                    "/<string:pms_property_uuid>",
                ],
                "GET",
            )
        ],
        output_param=Datamodel("pms.housekeeping.property.info"),
        auth="jwt_api_pms_housekeeping",
    )
    def get_property(self, pms_property_uuid):
        if check_api_housekeeping_access(self.env.user, pms_property_uuid):
            pms_property = self.env["pms.property"].sudo().search([("housekeeping_uuid", "=", pms_property_uuid)])
            PmsPropertyInfo = self.env.datamodels["pms.housekeeping.property.info"]
            res = PmsPropertyInfo(
                uuid=pms_property.housekeeping_uuid,
                name=pms_property.name,
                hotelImageUrl=url_image_pms_api_rest(
                    "pms.property", pms_property.id, "hotel_image_pms_api_rest"
                ),
                city=pms_property.city if pms_property.city else None,
                stateName=(
                    self.env["res.country.state"]
                    .search([("id", "=", pms_property.state_id.id)])
                    .name
                    if pms_property.state_id
                    else None
                ),
                timezone=pms_property.tz if pms_property.tz else None,
            )
            return res
