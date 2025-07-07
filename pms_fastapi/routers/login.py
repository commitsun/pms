from typing import Annotated

from fastapi import Depends, HTTPException, Response, status

from odoo.api import Environment
from odoo.exceptions import AccessDenied

from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.pms_fastapi.models.fastapi_endpoint import pms_api_router
from odoo.addons.pms_fastapi.schemas.pms_login import PmsLoginInput


@pms_api_router.post(
    "/login/",
    responses={
        401: {
            "description": "Unauthorized",
            "content": {"application/json": {"example": {"detail": "wrong user/pass"}}},
            204: {"model": None},
        }
    },
    tags=["login"],
)
async def login(user: PmsLoginInput, env: Annotated[Environment, Depends(odoo_env)]):
    user_record = env["res.users"].sudo().search([("login", "=", user.username)])

    if not user_record:
        raise HTTPException(
            status_code=401,
            detail="wrong user/pass",
        )
    try:
        user_record.with_user(user_record)._check_credentials(user.password, None)
    except AccessDenied as e:
        raise HTTPException(
            status_code=401,
            detail="wrong user/pass",
        ) from e

    validator = env["auth.jwt.validator"].sudo()._get_validator_by_name("api_pms")
    assert len(validator) == 1
    payload = {
        "username": user_record.login,
    }
    token = validator._encode(
        payload,
        secret=validator._get_jwt_cookie_secret(),
        expire=validator.cookie_max_age,
    )
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.set_cookie(
        key=validator.cookie_name,
        value=token,
        max_age=validator.cookie_max_age,
        path=validator.cookie_path or "/",
        secure=validator.cookie_secure,
        httponly=True,
    )
    return response
