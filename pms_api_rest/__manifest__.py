{
    "name": "API REST PMS",
    "author": "Commit [Sun], Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/pms",
    "category": "Generic Modules/Property Management System",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "pms",
        "base_rest",
        "base_rest_datamodel",
        "web",
        "auth_signup",
        "auth_jwt_login",
        "base_location",
        "l10n_es_aeat",
        "sql_export_excel",
        "feed_rss",
    ],
    "external_dependencies": {
        "python": ["jwt", "simplejson", "marshmallow", "jose"],
    },
    "data": [
        "security/ir.model.access.csv",
        "data/sql_reports.xml",
        "data/auth_jwt_validator.xml",
        "data/pms_app_reset_password_template.xml",
        "data/cron_jobs.xml",
        "views/pms_property_views.xml",
        "views/res_users_views.xml",
        "views/pms_room_type_class_views.xml",
        "views/product_template_views.xml",
        "views/pms_api_log_views.xml",
    ],
    "demo": [
        "demo/pms_api_rest_master_data.xml",
    ],
    "installable": True,
}
