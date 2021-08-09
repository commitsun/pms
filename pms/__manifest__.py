# Copyright 2019 Darío Lodeiros, Alexandre Díaz, Jose Luis Algara, Pablo Quesada
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "PMS (Property Management System)",
    "summary": "A property management system",
    "version": "14.0.2.15.2",
    "development_status": "Alpha",
    "category": "Generic Modules/Property Management System",
    "website": "https://github.com/OCA/pms",
    "author": "Commit [Sun], Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "depends": [
        "base",
        "mail",
        # "account_payment_return",
        # "email_template_qweb",
        "sale",
        "multi_pms_properties",
        "partner_identification",
        "partner_firstname",
        "partner_second_lastname",
        "partner_contact_gender",
        "partner_contact_birthdate",
        "partner_contact_nationality",
        # "partner_identification_unique_by_category",
    ],
    "data": [
        "security/pms_security.xml",
        "security/ir.model.access.csv",
        "data/cron_jobs.xml",
        "data/pms_sequence.xml",
        "data/pms_data.xml",
        "data/traveller_report_paperformat.xml",
        "report/pms_folio.xml",
        "report/pms_folio_templates.xml",
        "report/traveller_report_action.xml",
        # "templates/pms_email_template.xml",
        "data/menus.xml",
        "wizards/wizard_payment_folio.xml",
        "wizards/folio_make_invoice_advance_views.xml",
        "wizards/pms_booking_engine_views.xml",
        "wizards/wizard_folio_changes.xml",
        "views/pms_amenity_views.xml",
        "views/pms_amenity_type_views.xml",
        "views/pms_board_service_views.xml",
        "views/pms_board_service_room_type_views.xml",
        "views/pms_cancelation_rule_views.xml",
        "views/pms_checkin_partner_views.xml",
        "views/pms_ubication_views.xml",
        "views/pms_property_views.xml",
        "views/pms_reservation_views.xml",
        "views/pms_service_views.xml",
        "views/pms_service_line_views.xml",
        "views/pms_folio_views.xml",
        "views/pms_room_type_views.xml",
        "views/pms_room_views.xml",
        "views/pms_room_closure_reason_views.xml",
        "views/account_payment_views.xml",
        "views/account_move_views.xml",
        "views/account_bank_statement_views.xml",
        "views/res_users_views.xml",
        "views/pms_room_type_class_views.xml",
        "views/pms_availability_plan_views.xml",
        "views/pms_availability_plan_rule_views.xml",
        "views/pms_shared_room_views.xml",
        "views/res_partner_views.xml",
        "views/product_pricelist_views.xml",
        "views/product_pricelist_item_views.xml",
        "views/pms_sale_channel.xml",
        "views/product_template_views.xml",
        "views/webclient_templates.xml",
        "views/account_journal_views.xml",
        "views/folio_portal_templates.xml",
        "views/reservation_portal_templates.xml",
        "views/res_company_views.xml",
        "views/traveller_report_template.xml",
        "wizards/wizard_split_join_swap_reservation.xml",
        "wizards/wizard_massive_changes.xml",
        "wizards/wizard_advanced_filters.xml",
    ],
    "demo": [
        "demo/pms_master_data.xml",
        "demo/pms_folio.xml",
        "demo/pms_reservation.xml",
    ],
    "qweb": [
        "static/src/xml/pms_base_templates.xml",
        "static/src/xml/reservation_group_button_views.xml",
    ],
    "pre_init_hook": "pre_init_hook",
}
