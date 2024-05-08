import base64

from odoo import fields

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component


class PmsPropertyService(Component):
    _inherit = "base.rest.service"
    _name = "pms.property.service.roomdoo"
    _usage = "properties"
    _collection = "pms.services"

    @restapi.method(
        [
            (
                [
                    "/traveller-report",
                ],
                "GET",
            )
        ],
        input_param=Datamodel("pms.report.search.param", is_list=False),
        output_param=Datamodel("pms.report", is_list=False),
        auth="jwt_api_pms",
    )
    def traveller_report(self, pms_report_search_param):
        pms_property_id = pms_report_search_param.pmsPropertyId
        pms_property = self.env["pms.property"].search([("id", "=", pms_property_id)])
        date_from = fields.Date.from_string(pms_report_search_param.dateFrom)
        report_wizard = self.env["traveller.report.wizard"].create(
            {
                "date_target": date_from,
                "pms_property_id": pms_property_id,
            }
        )
        content = report_wizard.generate_checkin_list(
            pms_property_id=pms_property_id,
            date_target=date_from,
        )
        file_name = pms_property.institution_property_id + ".999"
        base64EncodedStr = base64.b64encode(str.encode(content))
        PmsResponse = self.env.datamodels["pms.report"]
        return PmsResponse(fileName=file_name, binary=base64EncodedStr)
