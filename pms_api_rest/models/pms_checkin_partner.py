from odoo import fields, models, api


class PmsCheckinPartner(models.Model):
    _inherit = "pms.checkin.partner"

    origin_input_data = fields.Selection(
        selection=[
            ("wizard", "Wizard"),
            ("form", "Form"),
            ("regular_customer", "Regular customer"),
            ("ocr", "OCR"),
            ("precheckin", "Precheckin"),
        ],
        string="Origin input data",
    )
