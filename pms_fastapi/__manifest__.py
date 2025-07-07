{
    "name": "PMS FastAPI",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "author": "Commit [Sun], Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/pms",
    "category": "Generic Modules/Property Management System",
    "license": "AGPL-3",
    "depends": [
        "fastapi",
        "auth_jwt_login",
    ],
    "data": [
        "security/pms_fastapi_groups.xml",
        "data/res_users.xml",
        "data/fastapi_endpoint.xml",
    ],
}
