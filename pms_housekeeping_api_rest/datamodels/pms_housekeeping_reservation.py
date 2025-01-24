from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel


class PmsHousekeepingReservationInput(Datamodel):
    _name = "pms.housekeeping.reservation.input"
    pmsPropertyUuid = fields.String(required=False, allow_none=True)


class PmsHousekeepingReservationInfo(Datamodel):
    _name = "pms.housekeeping.reservation.info"
    uuid = fields.String(required=False, allow_none=True)
    name = fields.String(required=False, allow_none=True)
    checkin = fields.String(required=False, allow_none=True)
    checkout = fields.String(required=False, allow_none=True)
    guests = fields.Integer(required=False, allow_none=True)
