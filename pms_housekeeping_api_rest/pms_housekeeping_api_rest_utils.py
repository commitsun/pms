from odoo.http import request
from odoo import _

from odoo.odoo.exceptions import AccessError


def check_api_housekeeping_access(user, property_uuid):
    """
    Verifies that the user has access to the property.
    """
    if not user.pms_property_id:
        raise AccessError(_("User has no property assigned"))
    if user.pms_property_id.housekeeping_uuid != property_uuid:
        raise AccessError(_("User has no access to the property"))
    return True


def url_image_pms_api_rest(model, record_id, field):
    rt_image_attach = (
        request.env["ir.attachment"]
        .sudo()
        .search(
            [
                ("res_model", "=", model),
                ("res_id", "=", record_id),
                ("res_field", "=", field),
            ]
        )
    )
    if rt_image_attach and not rt_image_attach.access_token:
        rt_image_attach.generate_access_token()
    result = (
        request.env["ir.config_parameter"].sudo().get_param("web.base.url")
        + "/web/image/%s?access_token=%s"
        % (rt_image_attach.id, rt_image_attach.access_token)
        if rt_image_attach
        else False
    )
    return result if result else ""
