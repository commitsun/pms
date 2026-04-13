from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    _deleted_xml_records = [
        "pms.view_partner_property_form",
        "pms.autoinvoicing_folios",
        "pms.autoinvoicing_downpayments",
        "pms.autoinvoice_folio_job_function",
        "pms.autovalidate_invoice_folio_job_function",
        "pms.channel_autoinvoicing_folios",
    ]
    openupgrade.delete_records_safely_by_xml_id(env, _deleted_xml_records)

    # autoinvoice_date moved from pms to pms_autoinvoice. Rename to a temp
    # column so pms doesn't lose the data; pms_autoinvoice pre_init_hook will
    # rename it back before the field is (re)created, avoiding a full recompute.
    if openupgrade.column_exists(env.cr, "folio_sale_line", "autoinvoice_date"):
        openupgrade.rename_columns(
            env.cr,
            {"folio_sale_line": [("autoinvoice_date", "autoinvoice_date_moved")]},
        )
