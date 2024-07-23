import uuid

from odoo import api, fields, models
from odoo.tools.safe_eval import time


class PmsCheckinPartner(models.Model):
    _inherit = "pms.checkin.partner"

    origin_input_data = fields.Selection(
        [
            ("wizard", "Wizard"),
            ("form", "Form"),
            ("regular_customer", "Regular Customer"),
            ("ocr", "OCR"),
            ("precheckin", "Precheckin"),
        ],
        string="Origin Input Data",
    )

    api_rest_id = fields.Char(string="API Rest ID", help="API Rest ID")

    @api.model
    def create(self, vals):
        result = super(PmsCheckinPartner, self).create(vals)
        self._generate_api_rest_id(result)
        return result

    @api.model
    def _generate_api_rest_id(self, reservation_record):
        if not reservation_record.api_rest_id:
            timestamp = int(time.time() * 1000)
            new_uuid = uuid.uuid4()
            unique_uuid = f"{new_uuid}_{timestamp}"
            reservation_record.api_rest_id = unique_uuid
