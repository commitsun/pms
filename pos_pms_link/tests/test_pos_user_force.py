# Copyright 2026 Commit [Sun]
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""The pos_user_force context reads in sudo for the point of sale only:
anybody else keeps their own access rights, so fields restricted to some
groups, such as the signup token, stay out of reach."""

from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPosUserForce(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        users = cls.env["res.users"].with_context(no_reset_password=True)
        cls.portal_user = users.create(
            {
                "name": "Portal",
                "login": "portal@example.org",
                "groups_id": [Command.set([cls.env.ref("base.group_portal").id])],
            }
        )
        cls.pos_user = users.create(
            {
                "name": "Cashier",
                "login": "cashier@example.org",
                "groups_id": [
                    Command.set([cls.env.ref("point_of_sale.group_pos_user").id])
                ],
            }
        )
        cls.guest = cls.env["res.partner"].create({"name": "Somebody Else"})
        cls.guest.signup_prepare()

    def _forced_read(self, user):
        return (
            self.env["res.partner"]
            .with_user(user)
            .with_context(pos_user_force=True)
            .search_read([("id", "=", self.guest.id)], ["signup_token"])
        )

    def test_a_portal_user_keeps_its_own_rights(self):
        with self.assertRaises(AccessError):
            self._forced_read(self.portal_user)

    def test_the_point_of_sale_reads_in_sudo(self):
        self.assertEqual(
            self._forced_read(self.pos_user)[0]["signup_token"],
            self.guest.signup_token,
        )
