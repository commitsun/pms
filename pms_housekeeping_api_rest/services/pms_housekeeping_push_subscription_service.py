from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component



class PmsHousekeepingPushSubscriptionService(Component):
    _inherit = "base.rest.service"
    _name = "pms.housekeeping.push.subscription.service"
    _usage = "subscribe"
    _collection = "pms.housekeeping.services"

    @restapi.method(
        [
            (
                [
                    "/",
                ],
                "POST",
            )
        ],
        input_param=Datamodel("pms.housekeeping.push.subscription.info", is_list=False),
        auth="jwt_api_pms_housekeeping",
    )
    def subscribe(self, pms_housekeeping_push_subscription_info_param):
        if pms_housekeeping_push_subscription_info_param.subscription:
            self.env["push.subscription"].sudo().create({
                "user_id": self.env.user.id,
                "subscription_info": pms_housekeeping_push_subscription_info_param.subscription
            })

    @restapi.method(
        [
            (
                [
                    "/",
                ],
                "DELETE",
            )
        ],
        auth="jwt_api_pms_housekeeping",
    )
    def unsubscribe(self):
        self.env["push.subscription"].sudo().search([("user_id", "=", self.env.user.id)]).unlink()
