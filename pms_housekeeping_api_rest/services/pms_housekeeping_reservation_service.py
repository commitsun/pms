from datetime import datetime

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component

from ..pms_housekeeping_api_rest_utils import check_api_housekeeping_access



class PmsHousekeepingPropertyService(Component):
    _inherit = "base.rest.service"
    _name = "pms.housekeeping.reservation.service"
    _usage = "reservations"
    _collection = "pms.housekeeping.services"

    @restapi.method(
        [
            (
                [
                    "/<string:reservation_uuid>",
                ],
                "GET",
            )
        ],
        input_param=Datamodel("pms.housekeeping.reservation.input", is_list=False),
        output_param=Datamodel("pms.housekeeping.reservation.info", is_list=False),
        auth="jwt_api_pms_housekeeping",
    )
    def get_reservation(self, reservation_uuid, reservation_search):
        if check_api_housekeeping_access(self.env.user, reservation_search.pmsPropertyUuid):
            reservation = self.env["pms.reservation"].sudo().search([("housekeeping_uuid", "=", reservation_uuid)])
            PmsHousekeepingReservationInfo = self.env.datamodels["pms.housekeeping.reservation.info"]
            checkin = datetime.combine(reservation.checkin, datetime.min.time()).isoformat()
            checkout = datetime.combine(reservation.checkout, datetime.min.time()).isoformat()
            guests = reservation.adults + reservation.children
            return PmsHousekeepingReservationInfo(
                uuid=reservation.housekeeping_uuid,
                name=reservation.name,
                checkin=checkin,
                checkout=checkout,
                guests=guests,
            )

