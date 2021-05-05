# Copyright 2021 Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import json
import logging

from odoo.addons.component.tests.common import SavepointComponentCase

_logger = logging.getLogger(__name__)


class TestWubookConnector(SavepointComponentCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # disable jobs
        # TODO: it breaks the folio creation with error:
        #   psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint
        #       "mail_followers_mail_followers_res_partner_res_model_id_uniq"
        #   DETAIL:  Key (res_model, res_id, partner_id)=(pms.folio, 79, 3) already exists.
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,  # no jobs thanks
            )
        )
        # common test data
        backend_type_values1 = {
            "name": "Backend Type Test 1",
            "model_type_id": cls.env.ref(
                "connector_pms_wubook.model_channel_wubook_backend_type"
            ).id,
            "room_type_class_ids": [
                (
                    0,
                    0,
                    {
                        "wubook_room_type": "1",  # Room
                        "room_type_shortname": "RO",
                    },
                ),
                (
                    0,
                    0,
                    {
                        "wubook_room_type": "2",
                        "room_type_shortname": "AP",
                    },
                ),
            ],
            "board_service_ids": [
                (
                    0,
                    0,
                    {
                        "wubook_board_service": "ai",
                        "board_service_shortname": "AI",
                    },
                ),
                (
                    0,
                    0,
                    {
                        "wubook_board_service": "hb",
                        "board_service_shortname": "HB",
                    },
                ),
                (
                    0,
                    0,
                    {
                        "wubook_board_service": "fb",
                        "board_service_shortname": "FB",
                    },
                ),
                (
                    0,
                    0,
                    {
                        "wubook_board_service": "bb",
                        "board_service_shortname": "BB",
                    },
                ),
            ],
        }
        cls.backend_type1 = cls.env["channel.wubook.backend.type"].create(
            backend_type_values1
        )
        cls.fake_credentials = {
            "username": "X",
            "password": "X",
            "property_code": "X",
            "pkey": "X",
        }
        cls.test_credentials = {}
        try:
            with open("wubook_auth.json", "r") as f:
                cls.test_credentials = json.load(f)
        except FileNotFoundError:
            pass
