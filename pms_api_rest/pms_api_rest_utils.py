from odoo import _
from odoo.http import request

BOARD_SERVICE_ACCOMODATION_ONLY = {
    "id": 0,
    "name": _("Solo Alojamiento"),
    "amount": 0,
    "boardServiceId": 0,
    "productIds": [],
}


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
