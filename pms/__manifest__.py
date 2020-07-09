# Copyright 2019 Darío Lodeiros, Alexandre Díaz, Jose Luis Algara, Pablo Quesada
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'pms',
    'summary': "A property management system",
    'version': '13.0.1.0.0',
    'development_status': 'Beta',
    'category': 'Generic Modules/Property Management System',
    'website': 'https://github.com/hootel/hootel',
    'author': 'Darío Lodeiros, '
              'Alexandre Díaz, '
              'Jose Luis Algara, '
              'Pablo Quesada ',
    'license': "AGPL-3",
    'application': True,
    'installable': True,
    'depends': [
        'base',
        'mail',
        'account_payment_return',
        'partner_firstname',
        'email_template_qweb'
    ],
    'data': [
        'security/pms_security.xml',
        'security/ir.model.access.csv',
        'data/cron_jobs.xml',
        'data/pms_data.xml',
        'data/pms_sequence.xml',
        'data/email_template_cancel.xml',
        'data/email_template_reserv.xml',
        'data/email_template_exit.xml',
        'report/pms_folio.xml',
        'report/pms_folio_templates.xml',
        'templates/pms_email_template.xml',
        'wizard/massive_changes.xml',
        'wizard/massive_price_reservation_days.xml',
        'wizard/service_on_day.xml',
        'wizard/split_reservation.xml',
        'wizard/wizard_reservation.xml',
        'views/general.xml',
        'data/menus.xml',
        'views/pms_amenity_views.xml',
        'views/pms_amenity_type_views.xml',
        'views/pms_board_service_views.xml',
        'views/pms_board_service_room_type_views.xml',
        'views/pms_cancelation_rule_views.xml',
        'views/pms_checkin_partner_views.xml',
        'views/pms_floor_views.xml',
        'views/pms_folio_views.xml',
        'views/pms_property_views.xml',
        'views/pms_reservation_views.xml',
        'views/pms_room_type_views.xml',
        'views/pms_room_views.xml',
        'views/pms_room_closure_reason_views.xml',
        'views/inherited_account_payment_views.xml',
        'views/inherited_account_invoice_views.xml',
        'views/inherited_res_users_views.xml',
        'views/pms_room_type_class_views.xml',
        'views/pms_room_type_restriction_views.xml',
        'views/pms_room_type_restriction_item_views.xml',
        'views/pms_service_views.xml',
        'views/pms_service_line_views.xml',
        'views/pms_shared_room_views.xml',
        'views/inherited_res_partner_views.xml',
        'views/inherited_product_pricelist_views.xml',
        'views/inherited_product_template_views.xml',
        'views/inherited_webclient_templates.xml',
        'wizard/folio_make_invoice_advance_views.xml',
    ],
    'demo': [
        'demo/pms_demo.xml'
    ],
    'qweb': [
        'static/src/xml/pms_base_templates.xml',
    ],
}