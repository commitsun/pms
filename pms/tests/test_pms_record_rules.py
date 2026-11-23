import datetime

from odoo.exceptions import AccessError
from odoo.tests.common import new_test_user

from .common import TestPms


class TestPmsSharedModelRules(TestPms):
    """Property record rules on models shared with other apps."""

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
        cls.pms_property3 = cls.env["pms.property"].create(
            {
                "name": "Property 3",
                "company_id": cls.company1.id,
                "default_pricelist_id": cls.pricelist1.id,
            }
        )
        cls.user_no_property = cls._create_user("rules_no_property")
        cls.user_p1 = cls._create_user("rules_p1", cls.pms_property1)
        cls.user_p2 = cls._create_user("rules_p2", cls.pms_property2)
        cls.user_p1_p3 = cls._create_user(
            "rules_p1_p3", cls.pms_property1 | cls.pms_property3
        )
        cls.user_p3 = cls._create_user("rules_p3", cls.pms_property3)
        cls.test_users = (
            cls.user_no_property
            | cls.user_p1
            | cls.user_p2
            | cls.user_p1_p3
            | cls.user_p3
        )

        cls.product = cls.env["product.product"].create(
            {"name": "Rules test product", "list_price": 5.0}
        )
        cls.pricelist_shared = cls.env["product.pricelist"].create(
            {
                "name": "Shared pricelist",
                "availability_plan_id": cls.availability_plan1.id,
            }
        )
        cls.item_shared = cls._create_item(10.0)
        cls.item_p1 = cls._create_item(20.0, cls.pms_property1)
        cls.item_p2 = cls._create_item(30.0, cls.pms_property2)
        cls.item_p1_p2 = cls._create_item(40.0, cls.pms_property1 | cls.pms_property2)
        cls.test_items = cls.item_shared | cls.item_p1 | cls.item_p2 | cls.item_p1_p2

    @classmethod
    def _create_user(
        cls, login, properties=None, groups="base.group_user,pms.group_pms_user"
    ):
        properties = properties or cls.env["pms.property"]
        return new_test_user(
            cls.env,
            login=login,
            groups=groups,
            company_id=cls.company1.id,
            company_ids=[(6, 0, cls.company1.ids)],
            pms_property_ids=[(6, 0, properties.ids)],
            pms_property_id=properties[:1].id,
        )

    @classmethod
    def _create_item(cls, price, properties=None):
        properties = properties or cls.env["pms.property"]
        return cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.pricelist_shared.id,
                "applied_on": "0_product_variant",
                "product_id": cls.product.id,
                "compute_price": "fixed",
                "fixed_price": price,
                "pms_property_ids": [(6, 0, properties.ids)],
            }
        )

    def _visible(self, records, user):
        # Values cached by the superuser would bypass the record rules
        self.env.invalidate_all()
        return records.with_user(user).search([("id", "in", records.ids)])

    # res.users

    def test_users_rule_user_without_property_sees_all_users(self):
        """An internal user without properties is not scoped by property."""
        self.assertEqual(
            self._visible(self.test_users, self.user_no_property), self.test_users
        )

    def test_users_rule_user_with_property_scoped(self):
        """A user with properties sees themselves, the users without
        properties and the users sharing at least one property."""
        self.assertEqual(
            self._visible(self.test_users, self.user_p1),
            self.user_p1 | self.user_no_property | self.user_p1_p3,
        )
        self.assertEqual(
            self._visible(self.test_users, self.user_p1_p3),
            self.user_p1_p3 | self.user_no_property | self.user_p1 | self.user_p3,
        )
        self.env.invalidate_all()
        with self.assertRaises(AccessError):
            self.user_p2.with_user(self.user_p1).check_access_rule("read")

    def test_users_rule_user_with_archived_properties_scoped(self):
        """A user whose properties are all archived is not treated as a user
        without properties: they see themselves and the users without
        properties only."""
        pms_property4 = self.env["pms.property"].create(
            {
                "name": "Property 4",
                "company_id": self.company1.id,
                "default_pricelist_id": self.pricelist1.id,
            }
        )
        user_p4 = self._create_user("rules_p4", pms_property4)
        pms_property4.action_archive()
        self.assertEqual(
            self._visible(self.test_users | user_p4, user_p4),
            user_p4 | self.user_no_property,
        )

    def test_users_rule_share_user_without_property_unchanged(self):
        """Portal users without properties keep the property scope: they
        only see themselves and the users without properties."""
        portal_user = self._create_user("rules_portal", groups="base.group_portal")
        self.assertEqual(
            self._visible(self.test_users | portal_user, portal_user),
            portal_user | self.user_no_property,
        )

    # product.pricelist.item

    def test_pricelist_item_rule_model(self):
        """The rule filters pricelist items, not availability plans."""
        rule = self.env.ref("pms.pms_product_pricelist_item_property_rule")
        self.assertEqual(rule.model_id.model, "product.pricelist.item")

    def test_pricelist_items_filtered_by_property(self):
        """Pricelist items without properties are shared; items with
        properties are only visible to users of those properties."""
        self.assertEqual(
            self._visible(self.test_items, self.user_p1),
            self.item_shared | self.item_p1 | self.item_p1_p2,
        )
        self.assertEqual(
            self._visible(self.test_items, self.user_p2),
            self.item_shared | self.item_p2 | self.item_p1_p2,
        )
        self.assertEqual(
            self._visible(self.test_items, self.user_no_property), self.item_shared
        )
        self.env.invalidate_all()
        with self.assertRaises(AccessError):
            self.item_p2.with_user(self.user_p1).check_access_rule("read")

    def test_pricelist_items_write_scoped_by_property(self):
        """A user allowed to edit pricelist items can only write, delete or
        create the shared items and the items of their properties."""
        manager_p1 = self._create_user(
            "rules_sale_manager_p1",
            self.pms_property1,
            groups="base.group_user,pms.group_pms_user,sales_team.group_sale_manager",
        )
        items = self.test_items.with_user(manager_p1)
        item_p2 = self.item_p2.with_user(manager_p1)
        # pms reads the item before writing a fixed price; min_quantity is
        # written without a prior read, so the write rule is exercised
        with self.assertRaises(AccessError):
            item_p2.write({"min_quantity": 2})
        with self.assertRaises(AccessError):
            item_p2.unlink()
        with self.assertRaises(AccessError):
            items.create(
                {
                    "pricelist_id": self.pricelist_shared.id,
                    "applied_on": "3_global",
                    "compute_price": "percentage",
                    "percent_price": 10.0,
                    "pms_property_ids": [(6, 0, self.pms_property2.ids)],
                }
            )
        self.env.invalidate_all()
        (items - item_p2).write({"min_quantity": 2})
        self.assertEqual(
            self.test_items.filtered(lambda item: item.min_quantity == 2),
            self.test_items - self.item_p2,
        )
        new_item = items.create(
            {
                "pricelist_id": self.pricelist_shared.id,
                "applied_on": "3_global",
                "compute_price": "percentage",
                "percent_price": 10.0,
                "pms_property_ids": [(6, 0, self.pms_property1.ids)],
            }
        )
        new_item.unlink()

    def test_pricelist_price_ignores_items_of_other_properties(self):
        """A price computed without sudo for a property the user is not
        allowed on ignores the items of that property."""
        today = datetime.date.today()
        self.env.invalidate_all()
        pricelist = self.pricelist_shared.with_user(self.user_p3)
        price = pricelist._get_product_price(
            self.product,
            1.0,
            consumption_date=today,
            pms_property_id=self.pms_property2.id,
        )
        # item_p2 and item_p1_p2 are hidden; only the shared item applies
        self.assertEqual(price, 10.0)
        price_sudo = pricelist.sudo()._get_product_price(
            self.product,
            1.0,
            consumption_date=today,
            pms_property_id=self.pms_property2.id,
        )
        self.assertEqual(price_sudo, 40.0)

    def test_pricelist_price_for_own_property(self):
        """Non-regression: the rule does not hide the user's own items from
        the price computation."""
        self.env.invalidate_all()
        price = self.pricelist_shared.with_user(self.user_p1)._get_product_price(
            self.product,
            1.0,
            consumption_date=datetime.date.today(),
            pms_property_id=self.pms_property1.id,
        )
        # item_p1 and item_p1_p2 both apply; the most recent one wins
        self.assertEqual(price, 40.0)
