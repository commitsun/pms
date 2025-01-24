from odoo.addons.base_rest.controllers import main


class BaseHousekeepingRestPrivateApiController(main.RestController):
    _root_path = "/api-housekeeping/"
    _collection_name = "pms.housekeeping.services"
    _default_auth = "public"
    _default_save_session = False
    _default_cors = "*"

