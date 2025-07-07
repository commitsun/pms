from typing import Annotated

from fastapi import Depends

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.pms_fastapi.models.fastapi_endpoint import pms_api_router
from odoo.addons.pms_fastapi.schemas.language import Language


@pms_api_router.get("/languages/", response_model=list[Language], tags=["db_info"])
async def get_server_languages(
    env: Annotated[Environment, Depends(odoo_env)]
) -> list[Language]:
    """
    Get server information including languages.
    """
    languages = env["res.lang"].sudo().search([])
    return [
        Language(id=lang.id, name=lang.name, iso_code=lang.code) for lang in languages
    ]
