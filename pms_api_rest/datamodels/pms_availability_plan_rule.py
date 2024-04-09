from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel
from odoo.addons.datamodel.fields import NestedModel


class PmsAvailabilityPlanRuleSearchParam(Datamodel):
    _name = "pms.availability.plan.rule.search.param"
    dateFrom = fields.String(required=True, allow_none=False)
    dateTo = fields.String(required=True, allow_none=False)
    pmsPropertyId = fields.Integer(required=True, allow_none=False)


class PmsAvailabilityPlanRuleInfo(Datamodel):
    _name = "pms.availability.plan.rule.info"
    id = fields.Integer(required=False, allow_none=True)
    pmsPropertyId = fields.Integer(required=True, allow_none=False)
    availabilityPlanId = fields.Integer(required=True, allow_none=False)
    roomTypeId = fields.Integer(required=True, allow_none=False)
    date = fields.String(required=True, allow_none=False)

    minStay = fields.Integer(required=False, allow_none=False)
    maxStay = fields.Integer(required=False, allow_none=False)
    minStayArrival = fields.Integer(required=False, allow_none=False)
    maxStayArrival = fields.Integer(required=False, allow_none=False)

    closed = fields.Boolean(required=False, allow_none=False)
    closedDeparture = fields.Boolean(required=False, allow_none=False)
    closedArrival = fields.Boolean(required=False, allow_none=False)

    quota = fields.Integer(required=False, allow_none=False)
    maxAvailability = fields.Integer(required=False, allow_none=False)


# TODO: REVIEW couldn't find any way to send input as array of rules
class PmsAvailabilityPlanRulesInfo(Datamodel):
    _name = "pms.availability.plan.rules.info"
    availabilityPlanRules = fields.List(NestedModel("pms.availability.plan.rule.info"))
