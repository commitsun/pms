# Copyright 2017  Dario Lodeiros
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class RoomClosureReason(models.Model):
    _name = "room.closure.reason"
    _description = "Cause of out of service"

    name = fields.Char(
        string="Name",
        help="The name that identifies the room closure reason",
        required=True,
        translate=True,
    )
    pms_property_ids = fields.Many2many(
        string="Properties",
        help="Properties with access to the element;"
        " if not set, all properties can access",
        comodel_name="pms.property",
        relation="pms_room_closure_reason_pms_property_rel",
        column1="room_closure_reason_type_id",
        column2="pms_property_id",
        ondelete="restrict",
    )
    description = fields.Text(
        string="Description",
        help="Explanation of the reason for closing a room",
        translate=True,
    )
    is_presale_lock = fields.Boolean(
        string="Pre-sale lock",
        help="used to block a room for possible future sale",
    )
    from_expiration_date = fields.Selection(
        selection=[
            ("checkout", "Checkout"),
            ("checkin", "Checkin"),
            ("created", "Created"),
        ],
        string="From expiration date",
        default="checkout",
    )
    expiration_action = fields.Selection(
        selection=[
            ("cancel", "Cancel"),
            ("notification", "Notification"),
        ],
        string="Action",
        default="cancel",
    )
    time_type = fields.Selection(
        selection=[
            ("hours", "Hours"),
            ("days", "Days"),
            ("months", "Months"),
        ],
        string="From expiration date",
        default="days",
    )
    time = fields.Integer(string="Time", help="Amount of time")
    moment = fields.Selection(
        string="Moment",
        help="Moment in relation to the action in which the email will be sent",
        selection=[
            ("before", "Before"),
            ("after", "After"),
            ("in_act", "In the act"),
        ],
        default="before",
    )
    active = fields.Boolean(
        string="Active", help="Indicates if the automated mail is active", default=True
    )
    separated_rooms = fields.Boolean(
        string="Separate rooms by folios",
        help="This option create a unique folio by each room",
    )
