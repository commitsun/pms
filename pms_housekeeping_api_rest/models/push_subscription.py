from odoo import fields, models, api


class PushSubscription(models.Model):
    _name = 'push.subscription'
    _description = 'Push Subscription'

    user_id = fields.Many2one('res.users', string='User', required=True)
    subscription_info = fields.Text(string='Subscription Info')
