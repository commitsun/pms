import logging

from odoo import _, fields
from odoo.exceptions import MissingError

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class PmsServiceService(Component):
    _inherit = "base.rest.service"
    _name = "pms.service.service.roomdoo"
    _usage = "services"
    _collection = "pms.services"

    @restapi.method(
        [
            (
                [
                    "/services-report",
                ],
                "GET",
            )
        ],
        input_param=Datamodel("pms.report.search.param", is_list=False),
        output_param=Datamodel("pms.report", is_list=False),
        auth="jwt_api_pms",
    )
    def services_report(self, pms_report_search_param):
        pms_property_id = pms_report_search_param.pmsPropertyId
        date_from = fields.Date.from_string(pms_report_search_param.dateFrom)
        date_to = fields.Date.from_string(pms_report_search_param.dateTo)
        query = self.env.ref("pms_api_rest_roomdoo.sql_export_services")
        if not query:
            raise MissingError(_("SQL query not found"))
        report_wizard = self.env["sql.file.wizard"].create({"sql_export_id": query.id})
        report_wizard.x_date_from = date_from
        report_wizard.x_date_to = date_to
        report_wizard.x_pms_property_id = pms_property_id
        if not report_wizard._fields.get(
            "x_date_from"
        ) or not report_wizard._fields.get("x_pms_property_id"):
            raise MissingError(
                _("The Query params was modifieds, please contact the administrator")
            )
        report_wizard.export_sql()
        file_name = report_wizard.file_name
        base64EncodedStr = report_wizard.binary_file
        PmsResponse = self.env.datamodels["pms.report"]
        return PmsResponse(fileName=file_name, binary=base64EncodedStr)
