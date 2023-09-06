import time

import werkzeug.exceptions
from jose import jwt

from odoo import _, http
from odoo.exceptions import AccessDenied

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component


class PmsLoginService(Component):
    _inherit = "base.rest.service"
    _name = "pms.auth.service"
    _usage = "login"
    _collection = "pms.services"

    @restapi.method(
        [
            (
                [
                    "/",
                ],
                "POST",
            )
        ],
        input_param=Datamodel("pms.api.rest.user.input", is_list=False),
        output_param=Datamodel("pms.api.rest.user.output", is_list=False),
        auth="public",
        cors="*",
    )
    def login(self, user):
        user_record = (
            self.env["res.users"].sudo().search([("login", "=", user.username)])
        )
        # formula = ms_now + ms in 1 sec * secs in 1 min
        minutes = 10000
        timestamp_expire_in_a_min = int(time.time() * 1000.0) + 1000 * 60 * minutes

        if not user_record:
            raise werkzeug.exceptions.Unauthorized(_("wrong user/pass"))
        try:
            user_record.with_user(user_record)._check_credentials(user.password, None)
        except AccessDenied:
            raise werkzeug.exceptions.Unauthorized(_("wrong user/pass"))

        validator = (
            self.env["auth.jwt.validator"].sudo()._get_validator_by_name("api_pms")
        )
        assert len(validator) == 1

        PmsApiRestUserOutput = self.env.datamodels["pms.api.rest.user.output"]

        token = jwt.encode(
            {
                "aud": "api_pms",
                "iss": "pms",
                "exp": timestamp_expire_in_a_min,
                "username": user.username,
                "password": user.password,
            },
            key=validator.secret_key,
            algorithm=validator.secret_algorithm,
        )
        avail_rule_names = []
        for avail_field in user_record.availability_rule_field_ids:
            avail_rule_names.append(avail_field.name)

        avatar_attach = self.env['ir.attachment'].sudo().search([
            ('res_model', '=', 'res.partner'),
            ('res_id', '=', user_record.partner_id.id),
            ('res_field', '=', 'image_128'),
        ])
        if avatar_attach and not avatar_attach.access_token:
            avatar_attach.generate_access_token()
        avatar_url = (
            http.request.env['ir.config_parameter']
                .sudo().get_param('web.base.url') +
            '/web/image/%s?access_token=%s' % (
                avatar_attach.id, avatar_attach.access_token
            ) if avatar_attach else False
        )
        return PmsApiRestUserOutput(
            token=token,
            expirationDate=timestamp_expire_in_a_min,
            userId=user_record.id,
            userName=user_record.name,
            userEmail=user_record.email if user_record.email else None,
            userPhone=user_record.phone if user_record.phone else None,
            defaultPropertyId=user_record.pms_property_id.id,
            defaultPropertyName=user_record.pms_property_id.name,
            userImageBase64=user_record.partner_id.image_1024
            if user_record.partner_id.image_1024
            else None,
            userImageUrl=avatar_url if avatar_url else "",
            isNewInterfaceUser=user_record.is_new_interface_app_user,
            availabilityRuleFields=avail_rule_names,
        )
