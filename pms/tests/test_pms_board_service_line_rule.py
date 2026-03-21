import datetime

from odoo.tests import tagged

from .common import TestPms


@tagged("standard", "nice")
class TestPmsBoardServiceLineRule(TestPms):
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

        cls.room_type1 = cls.env["pms.room.type"].create(
            {
                "pms_property_ids": [cls.pms_property1.id],
                "name": "Single",
                "default_code": "SIN",
                "class_id": cls.room_type_class1.id,
                "list_price": 30,
            }
        )
        cls.room_type2 = cls.env["pms.room.type"].create(
            {
                "pms_property_ids": [cls.pms_property2.id],
                "name": "Double",
                "default_code": "DBL",
                "class_id": cls.room_type_class1.id,
                "list_price": 40,
            }
        )

        cls.product1 = cls.env["product.product"].create(
            {"name": "Test Breakfast", "list_price": 10}
        )

        cls.board_service1 = cls.env["pms.board.service"].create(
            {
                "name": "Test Board Service",
                "default_code": "BS1",
            }
        )
        cls.board_service_line1 = cls.env["pms.board.service.line"].create(
            {
                "product_id": cls.product1.id,
                "pms_board_service_id": cls.board_service1.id,
                "amount": 10,
                "adults": True,
            }
        )

        cls.board_service_room_type1 = cls.env["pms.board.service.room.type"].create(
            {
                "pms_room_type_id": cls.room_type1.id,
                "pms_board_service_id": cls.board_service1.id,
                "pms_property_id": cls.pms_property1.id,
                "pricelist_ids": [(6, 0, [cls.pricelist1.id])],
            }
        )
        cls.board_service_room_type2 = cls.env["pms.board.service.room.type"].create(
            {
                "pms_room_type_id": cls.room_type2.id,
                "pms_board_service_id": cls.board_service1.id,
                "pms_property_id": cls.pms_property2.id,
            }
        )

        cls.board_service_room_type_line1 = (
            cls.board_service_room_type1.board_service_line_ids[0]
        )

    def _get_board_price(self, line, date_value):
        product = line.product_id.with_context(
            board_service_line_id=line.id,
            consumption_date=date_value,
        )
        return product.board_price

    def test_rule_date_range_applies(self):
        self.env["pms.board.service.room.type.line.rule"].create(
            {
                "board_service_room_type_line_id": (
                    self.board_service_room_type_line1.id
                ),
                "amount": 25,
                "date_start": datetime.date(2026, 2, 10),
                "date_end": datetime.date(2026, 2, 12),
            }
        )
        price = self._get_board_price(
            self.board_service_room_type_line1, datetime.date(2026, 2, 11)
        )
        self.assertEqual(price, 25)

    def test_rule_weekday_applies(self):
        self.env["pms.board.service.room.type.line.rule"].create(
            {
                "board_service_room_type_line_id": (
                    self.board_service_room_type_line1.id
                ),
                "amount": 30,
                "weekday_monday": True,
            }
        )
        monday = datetime.date(2026, 2, 9)  # Monday
        tuesday = datetime.date(2026, 2, 10)
        self.assertEqual(
            self._get_board_price(self.board_service_room_type_line1, monday), 30
        )
        self.assertEqual(
            self._get_board_price(self.board_service_room_type_line1, tuesday),
            self.board_service_room_type_line1.amount,
        )

    def test_rule_date_and_weekday_combined(self):
        self.env["pms.board.service.room.type.line.rule"].create(
            {
                "board_service_room_type_line_id": (
                    self.board_service_room_type_line1.id
                ),
                "amount": 40,
                "date_start": datetime.date(2026, 2, 9),
                "date_end": datetime.date(2026, 2, 11),
                "weekday_monday": True,
            }
        )
        monday = datetime.date(2026, 2, 9)
        tuesday = datetime.date(2026, 2, 10)
        self.assertEqual(
            self._get_board_price(self.board_service_room_type_line1, monday), 40
        )
        self.assertEqual(
            self._get_board_price(self.board_service_room_type_line1, tuesday),
            self.board_service_room_type_line1.amount,
        )

    def test_inactive_rule_ignored(self):
        self.env["pms.board.service.room.type.line.rule"].create(
            {
                "board_service_room_type_line_id": (
                    self.board_service_room_type_line1.id
                ),
                "amount": 55,
                "date_start": datetime.date(2026, 2, 10),
                "date_end": datetime.date(2026, 2, 12),
                "active": False,
            }
        )
        price = self._get_board_price(
            self.board_service_room_type_line1, datetime.date(2026, 2, 11)
        )
        self.assertEqual(price, self.board_service_room_type_line1.amount)

    def test_priority_highest_wins(self):
        self.env["pms.board.service.room.type.line.rule"].create(
            {
                "board_service_room_type_line_id": (
                    self.board_service_room_type_line1.id
                ),
                "amount": 60,
                "date_start": datetime.date(2026, 2, 10),
                "date_end": datetime.date(2026, 2, 12),
                "priority": 10,
            }
        )
        self.env["pms.board.service.room.type.line.rule"].create(
            {
                "board_service_room_type_line_id": (
                    self.board_service_room_type_line1.id
                ),
                "amount": 70,
                "date_start": datetime.date(2026, 2, 10),
                "date_end": datetime.date(2026, 2, 12),
                "priority": 20,
            }
        )
        price = self._get_board_price(
            self.board_service_room_type_line1, datetime.date(2026, 2, 11)
        )
        self.assertEqual(price, 70)

    def test_pricelist_ids_computed(self):
        rule = self.env["pms.board.service.room.type.line.rule"].create(
            {
                "board_service_room_type_line_id": (
                    self.board_service_room_type_line1.id
                ),
                "amount": 15,
                "weekday_monday": True,
            }
        )
        self.assertEqual(
            rule.pricelist_ids, self.board_service_room_type1.pricelist_ids
        )

    def test_wizard_default_weekdays_all_true(self):
        wizard = self.env["pms.board.service.line.rule.wizard"].create(
            {"board_service_id": self.board_service1.id, "amount": 12}
        )
        self.assertTrue(wizard.weekday_monday)
        self.assertTrue(wizard.weekday_tuesday)
        self.assertTrue(wizard.weekday_wednesday)
        self.assertTrue(wizard.weekday_thursday)
        self.assertTrue(wizard.weekday_friday)
        self.assertTrue(wizard.weekday_saturday)
        self.assertTrue(wizard.weekday_sunday)

    def test_wizard_creates_and_updates_rules(self):
        wizard = self.env["pms.board.service.line.rule.wizard"].create(
            {
                "board_service_id": self.board_service1.id,
                "pms_property_ids": [(6, 0, [self.pms_property1.id])],
                "amount": 22,
                "date_start": datetime.date(2026, 2, 10),
                "date_end": datetime.date(2026, 2, 12),
                "weekday_monday": True,
            }
        )
        wizard.action_create_rules()
        rule_model = self.env["pms.board.service.room.type.line.rule"]
        rule_count = rule_model.search_count(
            [
                (
                    "board_service_room_type_line_id",
                    "=",
                    self.board_service_room_type_line1.id,
                ),
                ("date_start", "=", datetime.date(2026, 2, 10)),
                ("date_end", "=", datetime.date(2026, 2, 12)),
                ("weekday_monday", "=", True),
            ]
        )
        self.assertEqual(rule_count, 1)

        wizard.amount = 33
        wizard.action_create_rules()
        rule = rule_model.search(
            [
                (
                    "board_service_room_type_line_id",
                    "=",
                    self.board_service_room_type_line1.id,
                ),
                ("date_start", "=", datetime.date(2026, 2, 10)),
                ("date_end", "=", datetime.date(2026, 2, 12)),
                ("weekday_monday", "=", True),
            ],
            limit=1,
        )
        self.assertEqual(rule.amount, 33)

    def test_available_properties_and_room_types(self):
        wizard = self.env["pms.board.service.line.rule.wizard"].create(
            {"board_service_id": self.board_service1.id, "amount": 12}
        )
        self.assertIn(self.pms_property1, wizard.available_property_ids)
        self.assertIn(self.pms_property2, wizard.available_property_ids)

        wizard.pms_property_ids = [(6, 0, [self.pms_property1.id])]
        self.assertIn(self.room_type1, wizard.available_room_type_ids)
        self.assertNotIn(self.room_type2, wizard.available_room_type_ids)

        self.env["pms.board.service.room.type"].create(
            {
                "pms_room_type_id": self.room_type1.id,
                "pms_board_service_id": self.board_service1.id,
                "pms_property_id": False,
            }
        )
        wizard2 = self.env["pms.board.service.line.rule.wizard"].create(
            {"board_service_id": self.board_service1.id, "amount": 12}
        )
        self.assertIn(self.pms_property1, wizard2.available_property_ids)
        self.assertIn(self.pms_property2, wizard2.available_property_ids)
