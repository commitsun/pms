from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel
from odoo.addons.datamodel.fields import NestedModel


class PmsPaymentReportInput(Datamodel):
    _name = "pms.payment.report"
    fileName = fields.String(required=False, allow_none=True)
    binary = fields.String(required=False, allow_none=True)
