
# Root.get_request = get_request
import json  # <--- Agregar esta línea

from werkzeug.exceptions import (
    BadRequest,
    Forbidden,
    HTTPException,
    InternalServerError,
    NotFound,
    Unauthorized,
)

import odoo
from odoo.exceptions import (
    AccessDenied,
    AccessError,
    MissingError,
    UserError,
    ValidationError,
)
from odoo.http import HttpRequest, Root, SessionExpiredException, Response
from odoo.loglevels import ustr

from odoo.addons.base_rest.http import (
    HttpRestRequest,
    _rest_services_routes,
    wrapJsonException,
)


class HttpRestRequestPms(HttpRestRequest):
    def __init__(self, httprequest):
        super(HttpRestRequestPms, self).__init__(httprequest)

    def _handle_exception(self, exception):

        if isinstance(exception, SessionExpiredException):
            response_data = {"error": "Unauthorized", "message": ustr(exception)}
            status_code = 401
        elif isinstance(exception, MissingError):
            response_data = {"error": "Not Found", "message": ustr(exception)}
            status_code = 404
        elif isinstance(exception, (AccessError, AccessDenied)):
            response_data = {"error": "Forbidden", "message": ustr(exception)}
            status_code = 403
        elif isinstance(exception, (UserError, ValidationError, ValueError)):
            response_data = {"error": "Bad Request", "message": ustr(exception)}
            status_code = 400
        elif isinstance(exception, HTTPException):
            response_data = {"error": exception.name, "message": ustr(exception.description)}
            status_code = exception.code
        else:
            response_data = {"error": "Internal Server Error", "message": ustr(exception)}
            status_code = 500

        return Response(
            json.dumps(response_data),
            status=status_code,
            content_type="application/json",
        )


ori_get_request = Root.get_request


def get_request(self, httprequest):
    db = httprequest.session.db
    if db and odoo.service.db.exp_db_exist(db):
        odoo.registry(db)
        rest_routes = _rest_services_routes.get(db, [])
        for root_path in rest_routes:
            if httprequest.path.startswith(root_path):
                return HttpRestRequestPms(httprequest)
    return ori_get_request(self, httprequest)


Root.get_request = get_request
