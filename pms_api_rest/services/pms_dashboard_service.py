from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo import fields
from datetime import datetime



class PmsDashboardServices(Component):
    _inherit = "base.rest.service"
    _name = "pms.dashboard.service"
    _usage = "dashboard"
    _collection = "pms.services"

    @restapi.method(
        [
            (
                [
                    "/pending-reservations",
                ],
                "GET",
            )
        ],
        input_param=Datamodel("pms.dashboard.range.dates.search.param"),
        output_param=Datamodel("pms.dashboard.pending.reservations", is_list=True),
        auth="jwt_api_pms",
    )
    def get_pending_reservations(self, pms_dashboard_search_param):
        dateFrom = fields.Date.from_string(pms_dashboard_search_param.dateFrom)
        dateTo = fields.Date.from_string(pms_dashboard_search_param.dateTo)

        self.env.cr.execute(
            f"""
            SELECT
            d.date,
            SUM(CASE WHEN r.checkin = d.date AND r.state IN ('confirm', 'arrival_delayed') THEN 1 ELSE 0
            END) AS reservations_pending_arrival,
            SUM(CASE WHEN r.checkin = d.date AND r.state = 'onboard' THEN 1 ELSE 0
            END) AS
            reservations_on_board,
            SUM(CASE WHEN r.checkout = d.date AND r.state IN ('onboard', 'departure_delayed') THEN 1 ELSE 0
            END) AS reservations_pending_departure,
            SUM(CASE WHEN r.checkout = d.date AND r.state = 'done' THEN 1 ELSE 0 END) AS reservations_completed
            FROM ( SELECT CURRENT_DATE + date AS date
            FROM generate_series(date '2023-08-30' - CURRENT_DATE, date '2023-09-30' - CURRENT_DATE) date) d
            LEFT JOIN pms_reservation r
            ON (r.checkin = d.date OR r.checkout = d.date)
            AND r.pms_property_id = 1
            AND r.reservation_type != 'out'
            GROUP BY d.date
            ORDER BY d.date;
            """,
            (
                dateFrom,
                dateTo,
                pms_dashboard_search_param.pmsPropertyId,
            ),
        )


        result = self.env.cr.dictfetchall()
        pending_reservations = []
        DashboardPendingReservations = self.env.datamodels["pms.dashboard.pending.reservations"]

        for item in result:
            pending_reservations.append(
                DashboardPendingReservations(
                    date=datetime.combine(item['date'], datetime.min.time()).isoformat(),
                    pendingArrivalReservations=item["reservations_pending_arrival"] if item["reservations_pending_arrival"] else 0,
                    completedArrivalReservations=item["reservations_on_board"] if item["reservations_on_board"] else 0,
                    pendingDepartureReservations=item["reservations_pending_departure"] if item["reservations_pending_departure"] else 0,
                    completedDepartureReservations=item["reservations_completed"] if item["reservations_completed"] else 0,
                )
            )
        return pending_reservations


    @restapi.method(
        [
            (
                [
                    "/occupancy",
                ],
                "GET",
            )
        ],
        input_param=Datamodel("pms.dashboard.search.param"),
        output_param=Datamodel("pms.dashboard.numeric.response"),
        auth="jwt_api_pms",
    )
    def get_occupancy(self, pms_dashboard_search_param):
        date_occupancy = fields.Date.from_string(pms_dashboard_search_param.date)

        self.env.cr.execute(
            f"""
            SELECT CEIL(l.num * 100.00 / tr.num_total_rooms)  AS occupancy
            FROM
            (
                SELECT COUNT(1) num_total_rooms
                FROM pms_room
                WHERE pms_property_id = %s
            ) tr,
            (
                SELECT COUNT(1) num
                FROM pms_reservation_line l
                INNER JOIN pms_reservation r  ON r.id = l.reservation_id
                WHERE r.reservation_type NOT IN ('out', 'staff')
                AND l.occupies_availability = true
                AND l.state != 'cancel'
                AND l.date = %s
                AND r.pms_property_id = %s
            ) l
            """,
            (
                pms_dashboard_search_param.pmsPropertyId,
                date_occupancy,
                pms_dashboard_search_param.pmsPropertyId,
            ),
        )

        result = self.env.cr.dictfetchall()
        DashboardNumericResponse = self.env.datamodels["pms.dashboard.numeric.response"]

        return DashboardNumericResponse(
            value=result[0]["occupancy"] if result else 0,
        )

    @restapi.method(
        [
            (
                [
                    "/billing",
                ],
                "GET",
            )
        ],
        input_param=Datamodel("pms.dashboard.range.dates.search.param"),
        output_param=Datamodel("pms.dashboard.numeric.response"),
        auth="jwt_api_pms",
    )
    def get_billing(self, pms_dashboard_search_param):
        date_from = fields.Date.from_string(pms_dashboard_search_param.dateFrom)
        date_to = fields.Date.from_string(pms_dashboard_search_param.dateTo)

        self.env.cr.execute(
            f"""
            SELECT SUM(l.price_day_total) billing
            FROM pms_reservation_line l INNER JOIN pms_reservation r ON l.reservation_id = r.id
            WHERE l.date BETWEEN %s AND %s
            AND l.occupies_availability = true
            AND l.state != 'cancel'
            AND l.pms_property_id = %s
            AND r.reservation_type NOT IN ('out', 'staff')
            """,
            (
                date_from,
                date_to,
                pms_dashboard_search_param.pmsPropertyId,
            ),
        )

        result = self.env.cr.dictfetchall()
        DashboardNumericResponse = self.env.datamodels["pms.dashboard.numeric.response"]

        return DashboardNumericResponse(
            value=result[0]["billing"] if result else 0,
        )


    @restapi.method(
        [
            (
                [
                    "/adr",
                ],
                "GET",
            )
        ],
        input_param=Datamodel("pms.dashboard.range.dates.search.param"),
        output_param=Datamodel("pms.dashboard.numeric.response"),
        auth="jwt_api_pms",
    )
    def get_adr(self, pms_dashboard_search_param):
        date_from = fields.Date.from_string(pms_dashboard_search_param.dateFrom)
        date_to = fields.Date.from_string(pms_dashboard_search_param.dateTo)

        pms_property = self.env["pms.property"].search([("id", "=", pms_dashboard_search_param.pmsPropertyId)])

        adr = pms_property._get_adr(date_from, date_to)

        DashboardNumericResponse = self.env.datamodels["pms.dashboard.numeric.response"]

        return DashboardNumericResponse(
            value=adr,
        )

    @restapi.method(
        [
            (
                [
                    "/revpar",
                ],
                "GET",
            )
        ],
        input_param=Datamodel("pms.dashboard.range.dates.search.param"),
        output_param=Datamodel("pms.dashboard.numeric.response"),
        auth="jwt_api_pms",
    )
    def get_revpar(self, pms_dashboard_search_param):
        date_from = fields.Date.from_string(pms_dashboard_search_param.dateFrom)
        date_to = fields.Date.from_string(pms_dashboard_search_param.dateTo)

        pms_property = self.env["pms.property"].search([("id", "=", pms_dashboard_search_param.pmsPropertyId)])

        revpar = pms_property._get_revpar(date_from, date_to)

        DashboardNumericResponse = self.env.datamodels["pms.dashboard.numeric.response"]

        return DashboardNumericResponse(
            value=revpar,
        )
