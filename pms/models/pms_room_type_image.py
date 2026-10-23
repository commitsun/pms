# Copyright 2026 Commit [Sun]
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PmsRoomTypeImage(models.Model):
    _name = "pms.room.type.image"
    _description = "Room Type Image"
    _inherit = "image.mixin"
    _order = "sequence, id"
    _check_pms_properties_auto = True

    name = fields.Char(
        string="Description",
        help="Alternative text of the image, read by screen readers and search "
        "engines",
        translate=True,
    )
    sequence = fields.Integer(
        help="Order of the image; the first one is the cover of the room type",
        default=10,
    )
    room_type_id = fields.Many2one(
        string="Room Type",
        help="Room type shown in the image",
        required=True,
        index=True,
        comodel_name="pms.room.type",
        ondelete="cascade",
    )
    pms_property_id = fields.Many2one(
        string="Property",
        help="Property whose room the image shows; if not set, it is shown in "
        "every property of the room type",
        index=True,
        comodel_name="pms.property",
        ondelete="restrict",
        check_pms_properties=True,
    )
    image_1920 = fields.Image(required=True)

    # Not check_pms_properties on room_type_id: it forbids an image without
    # property, the common one, on a room type restricted to some properties.
    @api.constrains("pms_property_id", "room_type_id")
    def _check_room_type_in_property(self):
        for image in self:
            room_type_properties = image.room_type_id.pms_property_ids
            if (
                image.pms_property_id
                and room_type_properties
                and image.pms_property_id not in room_type_properties
            ):
                raise ValidationError(
                    _("The room type %(room_type)s is not available in %(property)s.")
                    % {
                        "room_type": image.room_type_id.display_name,
                        "property": image.pms_property_id.display_name,
                    }
                )
