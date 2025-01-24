from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel



class PmsHousekeepingPushSubscriptionInfo(Datamodel):
    _name = "pms.housekeeping.push.subscription.info"
    subscription = fields.String(required=False, allow_none=True)
