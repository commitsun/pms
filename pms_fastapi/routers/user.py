from typing import Annotated

from fastapi import Depends

from odoo.api import Environment

from odoo.addons.fastapi_auth_jwt.dependencies import AuthJwtOdooEnv
from odoo.addons.pms_fastapi.models.fastapi_endpoint import pms_api_router
from odoo.addons.pms_fastapi.schemas.property import PropertyId
from odoo.addons.pms_fastapi.schemas.user import User

from ..pms_api_rest_utils import url_image_pms_api_rest


@pms_api_router.get("/user/", response_model=User, tags=["user"])
async def get_user_info(
    env: Annotated[Environment, Depends(AuthJwtOdooEnv(validator_name="api_pms"))]
) -> User:
    """
    Get current user basic information.
    """
    user = env.user
    return User(
        id=user.id,
        name=user.name,
        firstname=user.firstname or "",
        lastname=user.lastname or "",
        lastname2=user.lastname2 or "",
        email=user.email,
        phone=user.phone or "",
        image=url_image_pms_api_rest("res.partner", user.partner_id.id, "image_1024"),
        role=user.pms_api_user_role,
        defaultProperty=PropertyId(
            id=user.pms_property_id.id, name=user.pms_property_id.name
        ),
    )
