import logging

from odoo import fields

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class PmsTransactionService(Component):
    _inherit = "base.rest.service"
    _name = "pms.transaction.service"
    _usage = "transactions"
    _collection = "pms.services"

    @restapi.method(
        [
            (
                [
                    "/transactions-report",
                ],
                "GET",
            )
        ],
        input_param=Datamodel("pms.report.search.param", is_list=False),
        output_param=Datamodel("pms.report", is_list=False),
        auth="jwt_api_pms",
    )
    def transactions_report(self, pms_transaction_report_search_param):
        pms_property_id = pms_transaction_report_search_param.pmsPropertyId
        date_from = fields.Date.from_string(
            pms_transaction_report_search_param.dateFrom
        )
        date_to = fields.Date.from_string(pms_transaction_report_search_param.dateTo)

        report_wizard = self.env["cash.daily.report.wizard"].create(
            {
                "date_start": date_from,
                "date_end": date_to,
                "pms_property_id": pms_property_id,
            }
        )
        result = report_wizard._export()
        file_name = result["xls_filename"]
        base64EncodedStr = result["xls_binary"]
        PmsResponse = self.env.datamodels["pms.report"]
        return PmsResponse(fileName=file_name, binary=base64EncodedStr)
