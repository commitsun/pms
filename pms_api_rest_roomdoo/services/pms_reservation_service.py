import base64

from odoo import _, fields
from odoo.exceptions import MissingError

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component


class PmsReservationService(Component):
    _inherit = "base.rest.service"
    _name = "pms.reservation.service.roomdoo"
    _usage = "reservations"
    _collection = "pms.services"

    @restapi.method(
        [
            (
                [
                    "/kelly-report",
                ],
                "GET",
            )
        ],
        input_param=Datamodel("pms.report.search.param", is_list=False),
        output_param=Datamodel("pms.report", is_list=False),
        auth="jwt_api_pms",
    )
    def kelly_report(self, pms_report_search_param):
        pms_property_id = pms_report_search_param.pmsPropertyId
        date_from = fields.Date.from_string(pms_report_search_param.dateFrom)

        report_wizard = self.env["kellysreport"].create(
            {
                "date_start": date_from,
                "pms_property_id": pms_property_id,
            }
        )
        report_wizard.calculate_report()
        result = report_wizard._excel_export()
        file_name = result["xls_filename"]
        base64EncodedStr = result["xls_binary"]
        PmsResponse = self.env.datamodels["pms.report"]
        return PmsResponse(fileName=file_name, binary=base64EncodedStr)

    @restapi.method(
        [
            (
                [
                    "/arrivals-report",
                ],
                "GET",
            )
        ],
        input_param=Datamodel("pms.report.search.param", is_list=False),
        output_param=Datamodel("pms.report", is_list=False),
        auth="jwt_api_pms",
    )
    def arrivals_report(self, pms_report_search_param):
        pms_property_id = pms_report_search_param.pmsPropertyId
        date_from = fields.Date.from_string(pms_report_search_param.dateFrom)

        query = self.env.ref("pms_api_rest_roomdoo.sql_export_arrivals")
        if not query:
            raise MissingError(_("SQL query not found"))
        report_wizard = self.env["sql.file.wizard"].create({"sql_export_id": query.id})
        if not report_wizard._fields.get(
            "x_date_from"
        ) or not report_wizard._fields.get("x_pms_property_id"):
            raise MissingError(
                _("The Query params was modifieds, please contact the administrator")
            )
        report_wizard.x_date_from = date_from
        report_wizard.x_pms_property_id = pms_property_id

        report_wizard.export_sql()
        file_name = report_wizard.file_name
        base64EncodedStr = report_wizard.binary_file
        PmsResponse = self.env.datamodels["pms.report"]
        return PmsResponse(fileName=file_name, binary=base64EncodedStr)

    @restapi.method(
        [
            (
                [
                    "/departures-report",
                ],
                "GET",
            )
        ],
        input_param=Datamodel("pms.report.search.param", is_list=False),
        output_param=Datamodel("pms.report", is_list=False),
        auth="jwt_api_pms",
    )
    def departures_report(self, pms_report_search_param):
        pms_property_id = pms_report_search_param.pmsPropertyId
        date_from = fields.Date.from_string(pms_report_search_param.dateFrom)

        query = self.env.ref("pms_api_rest_roomdoo.sql_export_departures")
        if not query:
            raise MissingError(_("SQL query not found"))
        if query.state == "draft":
            query.button_validate_sql_expression()
        report_wizard = self.env["sql.file.wizard"].create({"sql_export_id": query.id})
        if not report_wizard._fields.get(
            "x_date_from"
        ) or not report_wizard._fields.get("x_pms_property_id"):
            raise MissingError(
                _("The Query params was modifieds, please contact the administrator")
            )
        report_wizard.x_date_from = date_from
        report_wizard.x_pms_property_id = pms_property_id

        report_wizard.export_sql()
        file_name = report_wizard.file_name
        base64EncodedStr = report_wizard.binary_file
        PmsResponse = self.env.datamodels["pms.report"]
        return PmsResponse(fileName=file_name, binary=base64EncodedStr)

    @restapi.method(
        [
            (
                [
                    "/<int:reservation_id>/checkin-report",
                ],
                "GET",
            )
        ],
        auth="jwt_api_pms",
        output_param=Datamodel("pms.report", is_list=False),
    )
    def print_all_checkins(self, reservation_id):
        reservations = False
        if reservation_id:
            reservations = self.env["pms.reservation"].sudo().browse(reservation_id)
        checkins = reservations.checkin_partner_ids.filtered(
            lambda x: x.state in ["precheckin", "onboard", "done"]
        )
        pdf = (
            self.env.ref("pms.action_traveller_report")
            .sudo()
            ._render_qweb_pdf(checkins.ids)[0]
        )
        base64EncodedStr = base64.b64encode(pdf)
        PmsResponse = self.env.datamodels["pms.report"]
        return PmsResponse(binary=base64EncodedStr)

    @restapi.method(
        [
            (
                [
                    "/<int:reservation_id>/checkin-partners/"
                    "<int:checkin_partner_id>/checkin-report",
                ],
                "GET",
            )
        ],
        auth="jwt_api_pms",
        output_param=Datamodel("pms.report", is_list=False),
    )
    def print_checkin(self, reservation_id, checkin_partner_id):
        reservations = False
        if reservation_id:
            reservations = self.env["pms.reservation"].sudo().browse(reservation_id)
        checkin_partner = reservations.checkin_partner_ids.filtered(
            lambda x: x.id == checkin_partner_id
        )
        pdf = (
            self.env.ref("pms.action_traveller_report")
            .sudo()
            ._render_qweb_pdf(checkin_partner.id)[0]
        )
        base64EncodedStr = base64.b64encode(pdf)
        PmsResponse = self.env.datamodels["pms.report"]
        return PmsResponse(binary=base64EncodedStr)
