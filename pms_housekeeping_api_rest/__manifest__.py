{
    "name": "PMS HOUSEKEEPING API REST",
    "author": "Commit [Sun], Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/pms",
    "category": "Generic Modules/Property Management System",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "pms_housekeeping",
        "base_rest",
        "base_rest_datamodel",
        "auth_signup",
        "auth_jwt_login",
    ],
    "external_dependencies": {
        "python": ["jwt", "simplejson", "marshmallow", "jose"],
    },
    "data": [
        "security/ir.model.access.csv",
        "data/auth_jwt_validator.xml",
        "views/res_users_views.xml",
        "views/pms_property_views.xml",
    ],
    "demo": [
        "demo/pms_housekeeping_api_rest_demo.xml",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
