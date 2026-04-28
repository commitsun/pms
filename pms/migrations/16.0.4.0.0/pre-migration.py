from openupgradelib import openupgrade

# Columns moved from pms to pms_autoinvoice. Rename to temp names so
# _process_end() cannot find and DROP them. The pms_autoinvoice
# pre_init_hook will rename them back before the fields are (re)created.
_COLUMNS_TO_MOVE = {
    "folio_sale_line": [("autoinvoice_date", "autoinvoice_date_moved")],
    "pms_property": [
        ("default_invoicing_policy", "default_invoicing_policy_moved"),
        ("invoicing_month_day", "invoicing_month_day_moved"),
        ("margin_days_autoinvoice", "margin_days_autoinvoice_moved"),
    ],
    "res_partner": [
        ("invoicing_policy", "invoicing_policy_moved"),
        ("invoicing_month_day", "invoicing_month_day_moved"),
        ("margin_days_autoinvoice", "margin_days_autoinvoice_moved"),
    ],
    "res_company": [
        ("pms_invoice_downpayment_policy", "pms_invoice_downpayment_policy_moved"),
    ],
    "account_journal": [
        ("avoid_autoinvoice_downpayment", "avoid_autoinvoice_downpayment_moved"),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    for table, columns in _COLUMNS_TO_MOVE.items():
        renames = [
            (old, new)
            for old, new in columns
            if openupgrade.column_exists(env.cr, table, old)
        ]
        if renames:
            openupgrade.rename_columns(env.cr, {table: renames})
