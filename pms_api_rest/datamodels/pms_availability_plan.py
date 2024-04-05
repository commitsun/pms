from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel


class PmsAvailabilityPlanInfo(Datamodel):
    _name = "pms.availability.plan.info"
    id = fields.Integer(required=True, allow_none=False)
    name = fields.String(required=True, allow_none=False)
    pmsPropertyIds = fields.List(fields.Integer(required=True, allow_none=True))
