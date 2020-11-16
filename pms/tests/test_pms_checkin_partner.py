import logging

from freezegun import freeze_time

from odoo import fields
from odoo.exceptions import ValidationError

from .common import TestHotel

_logger = logging.getLogger(__name__)


@freeze_time("2012-01-14")
class TestPmsCheckinPartner(TestHotel):
    @classmethod
    def arrange_single_checkin(cls):
        # Arrange for one checkin on one reservation
        cls.host1 = cls.env["res.partner"].create(
            {
                "name": "Miguel",
                "phone": "654667733",
                "email": "miguel@example.com",
            }
        )
        reservation_vals = {
            "checkin": "2012-01-14",
            "checkout": "2012-01-17",
            "room_type_id": cls.env.ref("pms.pms_room_type_3").id,
            "partner_id": cls.host1.id,
            "adults": 3,
            "pms_property_id": cls.env.ref("pms.main_pms_property").id,
        }
        demo_user = cls.env.ref("base.user_demo")
        cls.reservation_1 = (
            cls.env["pms.reservation"].with_user(demo_user).create(reservation_vals)
        )
        cls.checkin1 = cls.env["pms.checkin.partner"].create(
            {
                "partner_id": cls.host1.id,
                "reservation_id": cls.reservation_1.id,
            }
        )

    def test_auto_create_checkins(self):

        # ACTION
        self.arrange_single_checkin()
        checkins_count = len(self.reservation_1.checkin_partner_ids)

        # ASSERT
        self.assertEqual(
            checkins_count,
            3,
            "the automatic partner checkin was not created successful",
        )

    def test_auto_unlink_checkins(self):

        # ARRANGE
        self.arrange_single_checkin()

        # ACTION
        host2 = self.env["res.partner"].create(
            {
                "name": "Carlos",
                "phone": "654667733",
                "email": "carlos@example.com",
            }
        )
        self.reservation_1.checkin_partner_ids = [
            (
                0,
                False,
                {
                    "partner_id": host2.id,
                },
            )
        ]

        checkins_count = len(self.reservation_1.checkin_partner_ids)

        # ASSERT
        self.assertEqual(
            checkins_count,
            3,
            "the automatic partner checkin was not updated successful",
        )

    def test_onboard_checkin(self):

        # ARRANGE
        self.arrange_single_checkin()

        # ACT
        self.checkin1.action_on_board()

        # ASSERT
        self.assertEqual(
            self.checkin1.state,
            "onboard",
            "the partner checkin was not successful",
        )

    def test_onboard_reservation(self):

        # ARRANGE
        self.arrange_single_checkin()

        # ACT
        self.checkin1.action_on_board()

        # ASSERT
        self.assertEqual(
            self.reservation_1.state,
            "onboard",
            "the reservation checkin was not successful",
        )

    def test_premature_checkin(self):
        # ARRANGE
        self.arrange_single_checkin()
        self.reservation_1.write(
            {
                "checkin": "2012-01-15",
            }
        )

        # ACT & ASSERT
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.checkin1.action_on_board()

    def test_late_checkin(self):
        # ARRANGE
        self.arrange_single_checkin()
        self.reservation_1.write(
            {
                "checkin": "2012-01-13",
            }
        )

        # ACT
        self.checkin1.action_on_board()

        # ASSERT
        self.assertEqual(
            self.checkin1.arrival,
            fields.datetime.now(),
            "the late checkin has problems",
        )

    def test_too_many_people_checkin(self):
        # ARRANGE
        self.arrange_single_checkin()
        host2 = self.env["res.partner"].create(
            {
                "name": "Carlos",
                "phone": "654667733",
                "email": "carlos@example.com",
            }
        )
        host3 = self.env["res.partner"].create(
            {
                "name": "Enmanuel",
                "phone": "654667733",
                "email": "enmanuel@example.com",
            }
        )
        host4 = self.env["res.partner"].create(
            {
                "name": "Enrique",
                "phone": "654667733",
                "email": "enrique@example.com",
            }
        )
        self.env["pms.checkin.partner"].create(
            {
                "partner_id": host2.id,
                "reservation_id": self.reservation_1.id,
            }
        )
        self.env["pms.checkin.partner"].create(
            {
                "partner_id": host3.id,
                "reservation_id": self.reservation_1.id,
            }
        )
        # ACT & ASSERT
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.reservation_1.write(
                {
                    "checkin_partner_ids": [
                        (
                            0,
                            0,
                            {
                                "partner_id": host4.id,
                                "reservation_id": self.reservation_1.id,
                            },
                        )
                    ]
                }
            )

    @classmethod
    def arrange_folio_reservations(cls):
        # Arrange on one folio with 3 reservations
        demo_user = cls.env.ref("base.user_demo")
        cls.host1 = cls.env["res.partner"].create(
            {
                "name": "Miguel",
                "phone": "654667733",
                "email": "miguel@example.com",
            }
        )
        cls.host2 = cls.env["res.partner"].create(
            {
                "name": "Carlos",
                "phone": "654667733",
                "email": "carlos@example.com",
            }
        )
        cls.host3 = cls.env["res.partner"].create(
            {
                "name": "Enmanuel",
                "phone": "654667733",
                "email": "enmanuel@example.com",
            }
        )
        cls.host4 = cls.env["res.partner"].create(
            {
                "name": "Enrique",
                "phone": "654667733",
                "email": "enrique@example.com",
            }
        )
        folio_vals = {
            "partner_id": cls.host1.id,
        }
        cls.folio_1 = cls.env["pms.folio"].with_user(demo_user).create(folio_vals)
        reservation1_vals = {
            "checkin": "2012-01-14",
            "checkout": "2012-01-17",
            "room_type_id": cls.env.ref("pms.pms_room_type_3").id,
            "partner_id": cls.host1.id,
            "adults": 3,
            "pms_property_id": cls.env.ref("pms.main_pms_property").id,
            "folio_id": cls.folio_1.id,
        }
        reservation2_vals = {
            "checkin": "2012-01-14",
            "checkout": "2012-01-17",
            "room_type_id": cls.env.ref("pms.pms_room_type_2").id,
            "partner_id": cls.host1.id,
            "adults": 2,
            "pms_property_id": cls.env.ref("pms.main_pms_property").id,
            "folio_id": cls.folio_1.id,
        }
        reservation3_vals = {
            "checkin": "2012-01-14",
            "checkout": "2012-01-17",
            "room_type_id": cls.env.ref("pms.pms_room_type_2").id,
            "partner_id": cls.host1.id,
            "adults": 2,
            "pms_property_id": cls.env.ref("pms.main_pms_property").id,
            "folio_id": cls.folio_1.id,
        }
        cls.reservation_1 = (
            cls.env["pms.reservation"].with_user(demo_user).create(reservation1_vals)
        )
        cls.reservation_2 = (
            cls.env["pms.reservation"].with_user(demo_user).create(reservation2_vals)
        )
        cls.reservation_3 = (
            cls.env["pms.reservation"].with_user(demo_user).create(reservation3_vals)
        )

    def test_count_pending_arrival_persons(self):

        # ARRANGE
        self.arrange_folio_reservations()
        self.checkin1 = self.env["pms.checkin.partner"].create(
            {
                "partner_id": self.host1.id,
                "reservation_id": self.reservation_1.id,
            }
        )
        self.checkin2 = self.env["pms.checkin.partner"].create(
            {
                "partner_id": self.host2.id,
                "reservation_id": self.reservation_1.id,
            }
        )
        self.checkin3 = self.env["pms.checkin.partner"].create(
            {
                "partner_id": self.host3.id,
                "reservation_id": self.reservation_1.id,
            }
        )

        # ACT
        self.checkin1.action_on_board()
        self.checkin2.action_on_board()

        # ASSERT
        self.assertEqual(
            self.reservation_1.count_pending_arrival,
            1,
            "Fail the count pending arrival on reservation",
        )
        self.assertEqual(
            self.reservation_1.checkins_ratio,
            int(2 * 100 / 3),
            "Fail the checkins ratio on reservation",
        )

    def test_complete_checkin_data(self):

        # ARRANGE
        self.arrange_folio_reservations()

        # ACT
        self.checkin1 = self.env["pms.checkin.partner"].create(
            {
                "partner_id": self.host1.id,
                "reservation_id": self.reservation_1.id,
            }
        )
        self.checkin2 = self.env["pms.checkin.partner"].create(
            {
                "partner_id": self.host2.id,
                "reservation_id": self.reservation_1.id,
            }
        )
        pending_checkin_data = self.reservation_1.pending_checkin_data
        ratio_checkin_data = self.reservation_1.ratio_checkin_data
        # ASSERT
        self.assertEqual(
            pending_checkin_data,
            1,
            "Fail the count pending checkin data on reservation",
        )
        self.assertEqual(
            ratio_checkin_data,
            int(2 * 100 / 3),
            "Fail the checkins data ratio on reservation",
        )
