import time

from jose import jwt

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component

from ..pms_housekeeping_api_rest_utils import url_image_pms_api_rest


class PmsHousekeepingLoginService(Component):
    _inherit = "base.rest.service"
    _name = "pms.housekeeping.auth.service"
    _usage = "login"
    _collection = "pms.housekeeping.services"

    @restapi.method(
        [
            (
                [
                    "/",
                ],
                "POST",
            )
        ],
        input_param=Datamodel("pms.housekeeping.user.input", is_list=False),
        output_param=Datamodel("pms.housekeeping.user.output", is_list=False),
        auth="public",
        cors="*",
    )
    def login(self, user):
        user_record = (
            self.env["res.users"].sudo().search(
                [
                    ("login", "=", user.username),
                    ("user_role", "in", ["housekeeper", "housekeeping_manager"]),
                ]
            )
        )
        # formula = ms_now + 24 hours
        timestamp_expire_in_a_sec = int(time.time()) + 24 * 60 * 60

        user_record.with_user(user_record)._check_credentials(user.password, None)


        validator = (
            self.env["auth.jwt.validator"].sudo()._get_validator_by_name("api_pms_housekeeping")
        )
        assert len(validator) == 1

        PmsApiRestUserOutput = self.env.datamodels["pms.housekeeping.user.output"]

        token = jwt.encode(
            {
                "aud": "api_pms_housekeeping",
                "iss": "pms_housekeeping",
                "exp": timestamp_expire_in_a_sec,
                "username": user.username,
            },
            key=validator.secret_key,
            algorithm=validator.secret_algorithm,
        )

        return PmsApiRestUserOutput(
            uuid=user_record.housekeeping_uuid,
            token=token,
            expirationDate=timestamp_expire_in_a_sec,
            defaultPropertyUuid=user_record.pms_property_id.housekeeping_uuid,
            employeeUuid=user_record.employee_id.housekeeping_uuid,
        )
