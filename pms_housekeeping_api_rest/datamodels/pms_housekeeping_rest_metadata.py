from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel


class PmsHousekeepingRestMetadata(Datamodel):
    _name = "pms.housekeeping.rest.metadata"
    order = fields.String(required=False, allow_none=True)
    limit = fields.Integer(required=False, allow_none=True)
    offset = fields.Integer(required=False, allow_none=True)
    sort = fields.String(required=False, allow_none=True)
