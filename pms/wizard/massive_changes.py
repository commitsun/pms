# Copyright 2017  Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class MassiveChangesWizard(models.TransientModel):
    _name = 'pms.wizard.massive.changes'
    _description = 'Massive Changes'

    # Default methods
    @api.model
    def _get_default_pms_property(self):
        return self.env.user.pms_property_id

    # Fields declaration
    pms_property_id = fields.Many2one('pms.property', 'Property', required=True, default=_get_default_pms_property)
    pricelist_id = fields.Many2one(
        'product.pricelist', 'Pricelist Plan',
        domain="[('pricelist_type', '=', 'daily'), ('pms_property_ids.id', '=', context.get('pms_property_id'))]")
    restriction_id = fields.Many2one(
        'pms.room.type.restriction', 'Restriction Plan',
        domain="[('pms_property_id.id', '=', context.get('pms_property_id'))]")
    room_type_ids = fields.Many2many(
        'pms.room.type', string="Room Types",
        domain="[('pms_property_id.id', '=', context.get('pms_property_id'))]")

    section = fields.Selection([
        ('restrictions', 'Restrictions'),
        ('prices', 'Pricelist'),
    ], string='Section', default='prices')
    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date('End Date', required=True)
    dmo = fields.Boolean('Monday', default=True)
    dtu = fields.Boolean('Tuesday', default=True)
    dwe = fields.Boolean('Wednesday', default=True)
    dth = fields.Boolean('Thursday', default=True)
    dfr = fields.Boolean('Friday', default=True)
    dsa = fields.Boolean('Saturday', default=True)
    dsu = fields.Boolean('Sunday', default=True)
    applied_on = fields.Selection([
        ('0', 'Global'),
        ('1', 'Room Type'),
    ], string='Applied On', default='0')

    # Restriction fields
    change_min_stay = fields.Boolean(default=False, help="Mark for a massive change in this field.")
    min_stay = fields.Integer("Min. Stay")
    change_min_stay_arrival = fields.Boolean(default=False, help="Mark for a massive change in this field.")
    min_stay_arrival = fields.Integer("Min. Stay Arrival")
    change_max_stay = fields.Boolean(default=False, help="Mark for a massive change in this field.")
    max_stay = fields.Integer("Max. Stay")
    change_max_stay_arrival = fields.Boolean(default=False, help="Mark for a massive change in this field.")
    max_stay_arrival = fields.Integer("Max. Stay Arrival")
    change_closed = fields.Boolean(default=False, help="Mark for a massive change in this field.")
    closed = fields.Boolean('Closed')
    change_closed_departure = fields.Boolean(default=False, help="Mark for a massive change in this field.")
    closed_departure = fields.Boolean('Closed Departure')
    change_closed_arrival = fields.Boolean(default=False, help="Mark for a massive change in this field.")
    closed_arrival = fields.Boolean('Closed Arrival')

    # Pricelist fields
    price = fields.Char('Price', help="Can use '+','-' \
                                        or '%'...\nExamples:\n a) +12.3 \
                                        \t> Increase the price in 12.3\n \
                                        b) -1.45% \t> Substract 1.45%\n c) 45 \
                                        \t\t> Sets the price to 45")

    # Constraints and onchanges
    @api.constrains('pricelist_id')
    def _check_pricelist_id(self):
        for record in self:
            if record.pricelist_id.pricelist_type != 'daily':
                raise ValidationError(_("A daily pricelist plan is required for massive changes.") + " " +
                                      _("Please review the property configuration before proceed."))

    @api.constrains('hotepms_property_idl_id')
    def _check_pms_property_id(self):
        for record in self:
            if record.section == 'prices' and record.pricelist_id.pms_property_ids != record.pms_property_id:
                raise ValidationError(_("Mismatch between property and pricelist plan.") + " " +
                                      _("The pricelist plan does not belongs to the current property."))
            if record.section == 'restriction' and record.restriction_id.pms_property_id != record.pms_property_id:
                raise ValidationError(_("Mismatch between property and restriction plan.") + " " +
                                      _("The restriction plan does not belongs to the current property."))

    @api.onchange('date_start')
    def onchange_date_start(self):
        self.ensure_one()
        self.date_end = self.date_start

    # Action methods

    def _get_restrictions_values(self, record):
        self.ensure_one()
        vals = {}
        if record.change_min_stay:
            vals.update({'min_stay': record.min_stay})
        if record.change_min_stay_arrival:
            vals.update({'min_stay_arrival': record.min_stay_arrival})
        if record.change_max_stay:
            vals.update({'max_stay': record.max_stay})
        if record.change_max_stay_arrival:
            vals.update({'max_stay_arrival': record.max_stay_arrival})
        if record.change_closed:
            vals.update({'closed': record.closed})
        if record.change_closed_departure:
            vals.update({'closed_departure': record.closed_departure})
        if record.change_closed_arrival:
            vals.update({'closed_arrival': record.closed_arrival})
        return vals

    @api.model
    def _save_restrictions(self, ndate, room_types, record):
        pms_room_type_re_it_obj = self.env['pms.room.type.restriction.item']
        domain = [
            ('date', '>=', ndate.strftime(DEFAULT_SERVER_DATE_FORMAT)),
            ('date', '<=', ndate.strftime(DEFAULT_SERVER_DATE_FORMAT)),
            ('restriction_id', '=', record.restriction_id.id),
        ]
        for room_type in room_types:
            vals = self._get_restrictions_values(record)
            if not any(vals):
                continue

            rrest_item_ids = pms_room_type_re_it_obj.search(
                domain+[('room_type_id', '=', room_type.id)])
            if any(rrest_item_ids):
                rrest_item_ids.write(vals)
            else:
                vals.update({
                    'date': ndate.strftime(DEFAULT_SERVER_DATE_FORMAT),
                    'restriction_id': record.restriction_id.id,
                    'room_type_id': room_type.id,
                })
                pms_room_type_re_it_obj.create(vals)

    @api.model
    def _save_prices(self, ndate, room_types, record):
        product_pricelist_item_obj = self.env['product.pricelist.item']
        price = 0.0
        operation = 'a'
        if record.price[0] == '+' or record.price[0] == '-':
            if record.price[-1] == '%':
                price = float(record.price[1:-1])
                operation = 'ap' if (record.price[0] == '+') else 'sp'
            else:
                price = float(record.price[1:])
                operation = 'a' if (record.price[0] == '+') else 's'
        else:
            if record.price[-1] == '%':
                price = float(record.price[:-1])
                operation = 'np'
            else:
                price = float(record.price)
                operation = 'n'

        domain = [
            ('pricelist_id', '=', record.pricelist_id.id),
            ('date_start', '>=', ndate.strftime(
                DEFAULT_SERVER_DATE_FORMAT)),
            ('date_end', '<=', ndate.strftime(
                DEFAULT_SERVER_DATE_FORMAT)),
            ('compute_price', '=', 'fixed'),
            ('applied_on', '=', '1_product'),
        ]

        for room_type in room_types:
            prod_tmpl_id = room_type.product_id.product_tmpl_id
            pricelist_item_ids = product_pricelist_item_obj.search(
                domain+[('product_tmpl_id', '=', prod_tmpl_id.id)])
            if any(pricelist_item_ids):
                if operation != 'n':
                    for pli in pricelist_item_ids:
                        pli_price = pli.fixed_price
                        if operation == 'a':
                            pli.write({
                                'fixed_price': pli_price + price})
                        elif operation == 'ap':
                            pli.write({'fixed_price': pli_price + price * pli_price * 0.01})
                        elif operation == 's':
                            pli.write({
                                'fixed_price': pli_price - price})
                        elif operation == 'sp':
                            pli.write({'fixed_price': pli_price - price * pli_price * 0.01})
                        elif operation == 'np':
                            pli.write({'fixed_price': price * pli_price * 0.01})
                else:
                    pricelist_item_ids.write({'fixed_price': price})
            else:
                product_pricelist_item_obj.create({
                    'pricelist_id': record.pricelist_id.id,
                    'date_start': ndate.strftime(
                        DEFAULT_SERVER_DATE_FORMAT),
                    'date_end': ndate.strftime(
                        DEFAULT_SERVER_DATE_FORMAT),
                    'compute_price': 'fixed',
                    'applied_on': '1_product',
                    'product_tmpl_id': prod_tmpl_id.id,
                    'fixed_price': price,
                })

    @api.model
    def _save(self, ndate, room_types, record):
        if record.section == 'restrictions':
            self._save_restrictions(ndate, room_types, record)
        elif record.section == 'prices':
            self._save_prices(ndate, room_types, record)


    def _do_massive_change(self):
        pms_room_type_obj = self.env['pms.room.type']
        for record in self:
            date_start_dt = fields.Date.from_string(record.date_start)
            date_end_dt = fields.Date.from_string(record.date_end)
            # Use min '1' for same date
            diff_days = abs((date_end_dt - date_start_dt).days) + 1
            wedays = (record.dmo, record.dtu, record.dwe, record.dth,
                      record.dfr, record.dsa, record.dsu)

            # filter room types to the pricelist or restriction property
            room_types = record.room_type_ids if record.applied_on == '1' \
                else pms_room_type_obj.search([('pms_property_id', '=', record.pms_property_id.id)])

            for i in range(0, diff_days):
                ndate = date_start_dt + timedelta(days=i)
                if not wedays[ndate.timetuple()[6]]:
                    continue
                self._save(ndate, room_types, record)
        return True


    def massive_change(self):
        self._do_massive_change()
        return {
            "type": "ir.actions.do_nothing",
        }


    def massive_change_close(self):
        self._do_massive_change()
        return True

    # TODO: method deprecated and not used anywhere

    def is_valid_date(self, chkdate):
        self.ensure_one()
        wday = chkdate.timetuple()[6]
        wedays = (self.dmo, self.dtu, self.dwe, self.dth, self.dfr, self.dsa,
                  self.dsu)
        return (chkdate >= self.date_start and chkdate <= self.date_end
                and wedays[wday])
