from odoo import fields
from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component


class PmsPocService(Component):
    _inherit = "base.rest.service"
    _name = "pms.poc.xlsx"
    _usage = "poc"
    _collection = "pms.services"

    @restapi.method(
        [
            (
                [
                    "/",
                ],
                "GET",
            )
        ],
        output_param=Datamodel("pms.payment.report", is_list=False),
        auth="public",
    )
    def payment_report(self, ):
        pms_property_id = 1
        date_from = fields.Date.today()
        date_to = fields.Date.today()
        report_wizard = self.env["cash.daily.report.wizard"].sudo().create({
            "date_start": date_from,
            "date_end": date_to,
            "pms_property_id": pms_property_id,
        })
        result = report_wizard._export()
        file_name = result["xls_filename"]
        base64EncodedStr = result["xls_binary"]
        PmsResponse = self.env.datamodels["pms.payment.report"]
        # REVIEW: Reuse pms.report.info by modifying the fields
        # to support different types of documents?
        # proposal: contentBase64 = fields.String,
        # fileType = fields.String (pdf, xlsx, etc...)
        return PmsResponse(fileName=file_name, binary=base64EncodedStr)
