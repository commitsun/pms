from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(
        env.cr,
        [
            (
                "pms_api_rest.pms_reset_password_email",
                "pms_api_rest_roomdoo.pms_reset_password_email",
            ),
            (
                "pms_api_rest.date_from_field_variable_sql",
                "pms_api_rest_roomdoo.date_from_field_variable_sql",
            ),
            (
                "pms_api_rest.date_to_field_variable_sql",
                "pms_api_rest_roomdoo.date_to_field_variable_sql",
            ),
            (
                "pms_api_rest.pms_property_field_variable_sql",
                "pms_api_rest_roomdoo.pms_property_field_variable_sql",
            ),
            (
                "pms_api_rest.sql_export_departures",
                "pms_api_rest_roomdoo.sql_export_departures",
            ),
            (
                "pms_api_rest.sql_export_arrivals",
                "pms_api_rest_roomdoo.sql_export_arrivals",
            ),
            (
                "pms_api_rest.sql_export_services",
                "pms_api_rest_roomdoo.sql_export_services",
            ),
        ],
    )
