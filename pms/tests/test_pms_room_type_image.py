# Copyright 2026 Commit [Sun]
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import io

from PIL import Image

from odoo.exceptions import UserError, ValidationError

from .common import TestPms


class TestPmsRoomTypeImage(TestPms):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pms_property2 = cls.env["pms.property"].create(
            {
                "name": "Property 2",
                "company_id": cls.company1.id,
                "default_pricelist_id": cls.pricelist1.id,
            }
        )
        # A room type shared by two properties
        cls.room_type_double = cls.env["pms.room.type"].create(
            {
                "name": "Double",
                "default_code": "DBL_IMG",
                "class_id": cls.room_type_class1.id,
                "pms_property_ids": [
                    (6, 0, (cls.pms_property1 | cls.pms_property2).ids)
                ],
            }
        )
        buffer = io.BytesIO()
        Image.new("RGB", (8, 8), "blue").save(buffer, "PNG")
        cls.image_data = base64.b64encode(buffer.getvalue())

    def _create_image(self, sequence, pms_property=None):
        return self.env["pms.room.type.image"].create(
            {
                "room_type_id": self.room_type_double.id,
                "pms_property_id": pms_property.id if pms_property else False,
                "sequence": sequence,
                "image_1920": self.image_data,
            }
        )

    def _create_room(self, pms_property, name, size):
        return self.env["pms.room"].create(
            {
                "name": name,
                "pms_property_id": pms_property.id,
                "room_type_id": self.room_type_double.id,
                "capacity": 2,
                "size_m2": size,
            }
        )

    def test_images_of_the_property_and_common_ones(self):
        """
        The images of a room type in a property are its own ones and the ones
        without property, in order; those of other properties are left out.
        ------------
        A common image with sequence 20, one of property 1 with sequence 10 and one
        of property 2 with sequence 5: property 1 gets its own one and the common
        one, in that order.
        """
        # ARRANGE
        # With the relation already in the cache, new images are appended to it
        # in creation order
        self.assertFalse(self.room_type_double.room_type_image_ids)
        common = self._create_image(20)
        own = self._create_image(10, self.pms_property1)
        self._create_image(5, self.pms_property2)

        # ACT
        images = self.room_type_double.get_room_type_images(self.pms_property1.id)

        # ASSERT
        self.assertEqual(
            images.ids,
            [own.id, common.id],
            "The property should get its own image and then the common one",
        )

    def test_image_of_a_property_without_the_room_type(self):
        """
        An image cannot belong to a property the room type is not available in.
        """
        # ARRANGE
        pms_property3 = self.env["pms.property"].create(
            {
                "name": "Property 3",
                "company_id": self.company1.id,
                "default_pricelist_id": self.pricelist1.id,
            }
        )

        # ACT & ASSERT
        with self.assertRaises(ValidationError):
            self._create_image(10, pms_property3)

    def test_room_type_cannot_leave_a_property_with_its_images(self):
        """
        A property with images of a room type cannot be removed from it.
        """
        # ARRANGE
        self._create_image(10, self.pms_property2)

        # ACT & ASSERT
        with self.assertRaises(UserError):
            self.room_type_double.pms_property_ids = self.pms_property1

    def test_room_type_size_in_each_property(self):
        """
        The size of a room type in a property is the smallest one of its rooms
        there; rooms without size are ignored and 0 means unknown.
        ------------
        Property 1 has rooms of 18, 16 and unknown size; property 2 one of 25.
        """
        # ARRANGE
        self._create_room(self.pms_property1, "D101", 18.0)
        self._create_room(self.pms_property1, "D102", 16.0)
        self._create_room(self.pms_property1, "D103", 0.0)
        self._create_room(self.pms_property2, "D201", 25.0)
        pms_property3 = self.env["pms.property"].create(
            {
                "name": "Property 3",
                "company_id": self.company1.id,
                "default_pricelist_id": self.pricelist1.id,
            }
        )

        # ACT & ASSERT
        self.assertEqual(
            self.room_type_double.get_room_type_size(self.pms_property1.id), 16.0
        )
        self.assertEqual(
            self.room_type_double.get_room_type_size(self.pms_property2.id), 25.0
        )
        self.assertEqual(
            self.room_type_double.get_room_type_size(pms_property3.id), 0.0
        )
