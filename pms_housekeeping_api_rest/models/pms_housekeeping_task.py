from odoo import models, fields, api
import json
from pywebpush import webpush, WebPushException
import uuid



class PmsHouseKeepingTask(models.Model):
    _inherit = "pms.housekeeping.task"

    housekeeping_uuid = fields.Char('Housekeeping UUID', required=True, copy=False, index=True)

    @api.model
    def create(self, vals):
        vals['housekeeping_uuid'] = str(uuid.uuid4())
        res = super(PmsHouseKeepingTask, self).create(vals)
        self._send_notification(res)
        return res

    def _send_notification(self, task):
        subscriptions = self.env["push.subscription"].search([])

        title = "Nueva Tarea de Housekeeping"
        body = f"Se ha creado una nueva tarea en la habitación {task.room_id.name}."

        for subscription in subscriptions:
            try:
                subscription_info = json.loads(subscription.subscription_info)
                webpush(
                    subscription_info=subscription_info,
                    data=json.dumps({"title": title, "body": body}),
                    vapid_private_key="IS7tBHH2HFIgprH39-6IAdNyXclpiR__R_ZfZr-tIs0",
                    vapid_claims={
                        "sub": "mailto:braisterbutalino@gmail.com",
                    },
                )
            except WebPushException as e:
                print(f"Error enviando notificación: {e}")
