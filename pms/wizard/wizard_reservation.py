# Copyright 2018 Dario Lodeiros
# Copyright 2018 Alexandre Díaz <dev@redneboa.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import time
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class FolioWizard(models.TransientModel):
    _name = "pms.folio.wizard"
    _description = "Wizard for reservation groups"

    @api.model
    def _get_default_center_user(self):
        user = self.env["res.users"].browse(self.env.uid)
        return user.has_group("pms.group_pms_call")

    @api.model
    def _get_default_checkin(self):
        folio = False
        if "folio_id" in self._context:
            folio = self.env["pms.folio"].search(
                [("id", "=", self._context["folio_id"])]
            )
        if folio and folio.reservation_ids:
            return folio.reservation_ids[0].checkin
        return fields.Date.today()

    @api.model
    def _get_default_checkout(self):
        folio = False
        if "folio_id" in self._context:
            folio = self.env["pms.folio"].search(
                [("id", "=", self._context["folio_id"])]
            )
        if folio and folio.reservation_ids:
            return folio.reservation_ids[0].checkout
        return fields.Date.today()

    @api.model
    def _get_default_channel_type(self):
        user = self.env["res.users"].browse(self.env.uid)
        if user.has_group("pms.group_pms_call"):
            return "phone"

    @api.model
    def _get_default_pricelist(self):
        return self.env.user.pms_property_id.default_pricelist_id.id

    partner_id = fields.Many2one("res.partner", required=True, string="Customer")
    email = fields.Char("E-mail")
    mobile = fields.Char("Mobile")

    pricelist_id = fields.Many2one(
        "product.pricelist",
        string="Pricelist",
        required=True,
        default=_get_default_pricelist,
        help="Pricelist for current folio.",
    )
    checkin = fields.Date("Check In", required=True, default=_get_default_checkin)
    checkout = fields.Date("Check Out", required=True, default=_get_default_checkout)
    credit_card_details = fields.Text("Credit Card Details")
    internal_comment = fields.Text(string="Internal Folio Notes")
    reservation_wizard_ids = fields.One2many(
        "pms.reservation.wizard", "folio_wizard_id", string="Resevations"
    )
    service_wizard_ids = fields.One2many(
        "pms.service.wizard", "folio_wizard_id", string="Services"
    )
    total = fields.Float("Total", compute="_computed_total")
    date_order = fields.Date("Date Order", default=fields.Datetime.now)
    confirm = fields.Boolean("Confirm Reservations", default="1")
    autoassign = fields.Boolean("Autoassign", default="1")
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company
    )
    channel_type = fields.Selection(
        [("door", "Door"), ("mail", "Mail"), ("phone", "Phone"), ("call", "Call")],
        string="Sales Channel",
        default=_get_default_channel_type,
    )
    room_type_wizard_ids = fields.One2many(
        "pms.room.type.wizard", "folio_wizard_id", string="Room Types"
    )

    def assign_rooms(self):
        self.assign = True

    @api.onchange("pricelist_id")
    def onchange_pricelist_id(self):
        if self.pricelist_id:
            self.onchange_checks()

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        if self.partner_id:
            vals = {}
            pricelist = (
                self.partner_id.property_product_pricelist
                and self.partner_id.property_product_pricelist.id
                or self.env.user.pms_property_id.default_pricelist_id.id
            )
            vals.update(
                {
                    "pricelist_id": pricelist,
                    "email": self.partner_id.email,
                    "mobile": self.partner_id.mobile,
                }
            )
            self.update(vals)

    @api.onchange("autoassign")
    def create_reservations(self):
        self.ensure_one()
        cmds = [(5, 0, 0)]
        for line in self.room_type_wizard_ids:
            if line.rooms_num == 0:
                continue
            if line.rooms_num > line.max_rooms:
                raise ValidationError(_("Too many rooms!"))
            elif line.room_type_id:
                occupied = self.env["pms.reservation"].get_reservations(
                    line.checkin,
                    (
                        fields.Date.from_string(line.checkout) - timedelta(days=1)
                    ).strftime(DEFAULT_SERVER_DATE_FORMAT),
                )
                rooms_occupied = occupied.mapped("room_id.id")
                free_rooms = self.env["pms.room"].search(
                    [
                        ("id", "not in", rooms_occupied),
                        ("room_type_id.id", "=", line.room_type_id.id),
                    ],
                    order="sequence",
                    limit=line.rooms_num,
                )
                room_ids = free_rooms.mapped("id")
                room_list = self.env["pms.room"].search([("id", "in", room_ids)])
                checkin_dt = fields.Date.from_string(line.checkin)
                checkout_dt = fields.Date.from_string(line.checkout)
                nights = abs((checkout_dt - checkin_dt).days)
                for room in room_list:
                    adults = (
                        self.env["pms.room"].search([("id", "=", room.id)]).capacity
                    )
                    cmds.append(
                        (
                            0,
                            False,
                            {
                                "checkin": line.checkin,
                                "checkout": line.checkout,
                                "discount": line.discount,
                                "room_id": room.id,
                                "nights": nights,
                                "adults": adults,
                                "folio_wizard_id": self.id,
                                "board_service_room_id": line.board_service_room_id,
                                "children": 0,
                                "room_type_id": line.room_type_id,
                                "price": line.price,
                            },
                        )
                    )
        self.reservation_wizard_ids = cmds

    @api.onchange("checkin", "checkout")
    def onchange_checks(self):
        """
        When you change checkin or checkout it will checked it
        and update the qty of folio line
        -----------------------------------------------------------------
        @param self: object pointer
        """
        self.ensure_one()
        tz_property = self.env.user.pms_property_id.tz
        today = fields.Date.context_today(self.with_context(tz=tz_property))
        checkin_dt = (
            fields.Date.from_string(today)
            if not self.checkin
            else fields.Date.from_string(self.checkin)
        )
        checkout_dt = (
            fields.Date.from_string(today)
            if not self.checkout
            else fields.Date.from_string(self.checkout)
        )
        if checkin_dt >= checkout_dt:
            checkout_dt = checkin_dt + timedelta(days=1)

        checkin_str = checkin_dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
        checkout_str = checkout_dt.strftime(DEFAULT_SERVER_DATE_FORMAT)

        cmds = [(5, 0, 0)]
        room_type_ids = self.env["pms.room.type"].search([])
        for room_type in room_type_ids:
            cmds.append(
                (
                    0,
                    False,
                    {
                        "room_type_id": room_type.id,
                        "folio_wizard_id": self.id,
                        "checkin": checkin_str,
                        "checkout": checkout_str,
                    },
                )
            )
        self.update(
            {
                "checkin": checkin_str,
                "checkout": checkout_str,
                "room_type_wizard_ids": cmds,
            }
        )
        for room_type in self.room_type_wizard_ids:
            room_type.update_price()

    @api.depends(
        "room_type_wizard_ids.total_price",
        "reservation_wizard_ids.price",
        "reservation_wizard_ids",
        "service_wizard_ids.price_total",
    )
    def _computed_total(self):
        total = 0
        for line in self.service_wizard_ids:
            total += line.price_total

        if not self.reservation_wizard_ids:
            for line in self.room_type_wizard_ids:
                total += line.total_price
        else:
            for line in self.reservation_wizard_ids:
                total += line.price
        self.total = total

    def create_folio(self):
        self.ensure_one()
        if not self.partner_id:
            raise ValidationError(_("We need know the customer!"))
        reservations = [(5, False, False)]
        services = []
        if self.autoassign:
            self.create_reservations()
        for line in self.reservation_wizard_ids:
            services_room = []
            for product in line.product_ids:
                services_room.append((0, False, {"product_id": product.id}))
            reservations.append(
                (
                    0,
                    False,
                    {
                        "room_id": line.room_id.id,
                        "adults": line.adults,
                        "children": line.children,
                        "checkin": line.checkin,
                        "checkout": line.checkout,
                        "discount": line.discount,
                        "room_type_id": line.room_type_id.id,
                        "board_service_room_id": line.board_service_room_id.id,
                        "to_assign": line.to_assign,
                        "service_ids": services_room,
                        # REVIEW: Create folio with reservations dont respect the pricelist_id on folio dict
                        "pricelist_id": self.pricelist_id.id,
                    },
                )
            )
        for line in self.service_wizard_ids:
            services.append(
                (
                    0,
                    False,
                    {
                        "product_id": line.product_id.id,
                        "discount": line.discount,
                        "price_unit": line.price_unit,
                        "product_qty": line.product_uom_qty,
                    },
                )
            )
        if not self.reservation_wizard_ids:
            raise ValidationError(_("We cant create avoid folio"))
        vals = {
            "partner_id": self.partner_id.id,
            "channel_type": self.channel_type,
            "reservation_ids": reservations,
            "service_ids": services,
            "pricelist_id": self.pricelist_id.id,
            "internal_comment": self.internal_comment,
            "credit_card_details": self.credit_card_details,
            "email": self.email,
            "mobile": self.mobile,
        }
        newfol = self.env["pms.folio"].create(vals)
        if self.confirm:
            newfol.reservation_ids.confirm()
        action = self.env.ref("pms.open_pms_folio1_form_tree_all").read()[0]
        if newfol:
            action["views"] = [(self.env.ref("pms.pms_folio_view_form").id, "form")]
            action["res_id"] = newfol.id
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action


class PmsRoomTypeWizards(models.TransientModel):
    _name = "pms.room.type.wizard"
    _description = "Virtual Room Type to Reserve Groups"

    def _get_default_checkin(self):
        return self.folio_wizard_id.checkin

    @api.model
    def _get_default_checkout(self):
        return self.folio_wizard_id.checkout

    room_type_id = fields.Many2one("pms.room.type", string="Rooms Type")
    rooms_num = fields.Integer("Number of Rooms")
    max_rooms = fields.Integer("Max", compute="_compute_max")
    price = fields.Float(string="Price by Room")
    total_price = fields.Float(
        string="Total Price", compute="_compute_total", store="True"
    )
    folio_wizard_id = fields.Many2one("pms.folio.wizard")
    discount = fields.Float("discount")
    min_stay = fields.Integer("Min. Days", compute="_compute_max")
    checkin = fields.Date("Check In", required=True, default=_get_default_checkin)
    checkout = fields.Date("Check Out", required=True, default=_get_default_checkout)
    can_confirm = fields.Boolean(compute="_can_confirm")
    board_service_room_id = fields.Many2one(
        "pms.board.service.room.type", string="Board Service"
    )

    @api.onchange("rooms_num")
    def domain_board_service(self):
        for line in self:
            board_service_room_ids = []
            if line.room_type_id:
                pricelist_id = self.folio_wizard_id.pricelist_id.id
                board_services_room_type = self.env[
                    "pms.board.service.room.type"
                ].search(
                    [
                        ("pms_room_type_id", "=", self.room_type_id.id),
                        ("pricelist_id", "in", (pricelist_id, False)),
                    ]
                )
                board_service_room_ids = board_services_room_type.ids
            domain_boardservice = [("id", "in", board_service_room_ids)]
            return {"domain": {"board_service_room_id": domain_boardservice}}

    def _can_confirm(self):
        for record in self:
            date_start = fields.Date.from_string(record.checkin)
            date_end = fields.Date.from_string(record.checkout)
            date_diff = abs((date_end - date_start).days)
            record.can_confirm = record.max_rooms > 0 and record.min_stay <= date_diff

    def _compute_max(self):
        # REVIEW: This methid has a incorrect dependencies with pms_channel_conector
        # because use avail model defined on this module
        for res in self:
            user = self.env["res.users"].browse(self.env.uid)
            date_start = fields.Date.from_string(res.checkin)
            date_end = fields.Date.from_string(res.checkout)
            date_diff = abs((date_end - date_start).days)
            minstay_restrictions = self.env["pms.room.type.restriction.item"].search(
                [("room_type_id", "=", res.room_type_id.id),]
            )
            avail_restrictions = self.env["pms.room.type.availability"].search(
                [("room_type_id", "=", res.room_type_id.id)]
            )
            real_max = len(
                self.env["pms.room.type.availability"].rooms_available(
                    res.checkin,
                    (
                        fields.Date.from_string(res.checkout) - timedelta(days=1)
                    ).strftime(DEFAULT_SERVER_DATE_FORMAT),
                    res.room_type_id.id,
                )
            )
            res.real_avail = real_max
            avail = 100000
            min_stay = 0
            dates = []
            for i in range(0, date_diff):
                ndate_dt = date_start + timedelta(days=i)
                ndate_str = ndate_dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
                dates.append(ndate_str)
                if minstay_restrictions:
                    date_min_days = minstay_restrictions.filtered(
                        lambda r: r.date == ndate_str
                    ).min_stay
                    if date_min_days > min_stay:
                        min_stay = date_min_days
                if user.has_group("pms.group_pms_call"):
                    max_avail = real_max
                    restriction = False
                    if avail_restrictions:
                        restriction = avail_restrictions.filtered(
                            lambda r: r.date == ndate_str
                        )
                        if restriction:
                            if restriction.channel_bind_ids[0]:
                                max_avail = restriction.channel_bind_ids[
                                    0
                                ].channel_avail
                    if not restriction and res.room_type_id.channel_bind_ids:
                        if res.room_type_id.channel_bind_ids[0]:
                            max_avail = res.room_type_id.channel_bind_ids[
                                0
                            ].default_availability
                    if max_avail < avail:
                        avail = min(max_avail, real_max)
                else:
                    avail = real_max

            if avail < 100000 and avail > 0:
                res.max_rooms = avail
            else:
                res.max_rooms = 0
            if min_stay > 0:
                res.min_stay = min_stay

    @api.depends("rooms_num", "price")
    def _compute_total(self):
        for res in self:
            res.total_price = res.price * res.rooms_num

    @api.onchange(
        "rooms_num",
        "discount",
        "price",
        "board_service_room_id",
        "room_type_id",
        "checkin",
        "checkout",
    )
    def update_price(self):
        for record in self:
            if record.rooms_num > record.max_rooms:
                raise ValidationError(_("There are not enough rooms!"))
            checkin = record.checkin or record.folio_wizard_id.checkin
            checkout = record.checkout or record.folio_wizard_id.checkout
            chkin_utc_dt = fields.Date.from_string(checkin)
            chkout_utc_dt = fields.Date.from_string(checkout)
            if chkin_utc_dt >= chkout_utc_dt:
                chkout_utc_dt = chkin_utc_dt + timedelta(days=1)
            nights = abs((chkout_utc_dt - chkin_utc_dt).days)
            pricelist_id = self.folio_wizard_id.pricelist_id.id
            res_price = 0
            for i in range(0, nights):
                ndate = chkin_utc_dt + timedelta(days=i)
                ndate_str = ndate.strftime(DEFAULT_SERVER_DATE_FORMAT)
                product = record.room_type_id.product_id.with_context(
                    lang=record.folio_wizard_id.partner_id.lang,
                    partner=record.folio_wizard_id.partner_id.id,
                    quantity=1,
                    date=ndate_str,
                    pricelist=pricelist_id,
                    uom=record.room_type_id.product_id.uom_id.id,
                )
                res_price += product.price

            board_service = record.board_service_room_id
            if board_service:
                if board_service.price_type == "fixed":
                    board_price = (
                        board_service.amount * record.room_type_id.capacity * nights
                    )
                    res_price += board_price
                else:
                    res_price += (res_price * board_service.amount) * 0.01
            price = res_price - ((res_price * record.discount) * 0.01)
            vals = {
                "checkin": checkin,
                "checkout": checkout,
                "price": price,
            }
            record.update(vals)


class ReservationWizard(models.TransientModel):
    _name = "pms.reservation.wizard"
    _description = "Virtual Reservation to Groups"
    _rec_name = "room_id"

    room_id = fields.Many2one("pms.room", string="Room")
    folio_wizard_id = fields.Many2one("pms.folio.wizard")
    adults = fields.Integer("Adults", help="List of adults there in guest list. ")
    children = fields.Integer(
        "Children", help="Number of children there in guest list."
    )
    checkin = fields.Date("Check In", required=True)
    checkout = fields.Date("Check Out", required=True)
    room_type_id = fields.Many2one("pms.room.type", string="Room Type", required=True)
    nights = fields.Integer("Nights", readonly=True)
    price = fields.Float(string="Total")
    partner_id = fields.Many2one(related="folio_wizard_id.partner_id")
    discount = fields.Float("discount")
    to_assign = fields.Boolean(compute="_compute_assign")
    product_ids = fields.Many2many("product.product", string="Products")
    board_service_room_id = fields.Many2one(
        "pms.board.service.room.type", string="Board Service"
    )

    def _compute_assign(self):
        for rec in self:
            user = self.env["res.users"].browse(self.env.uid)
            if user.has_group("pms.group_pms_call"):
                rec.to_assign = True

    @api.onchange("room_id")
    def onchange_room_id(self):
        for line in self:
            if line.checkin and line.checkout:
                if line.adults == 0:
                    line.adults = line.room_id.capacity
                line.room_type_id = line.room_id.room_type_id.id
                checkout_dt = fields.Date.from_string(line.checkout)
                checkout_dt -= timedelta(days=1)
                occupied = self.env["pms.reservation"].get_reservations(
                    line.checkin, checkout_dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
                )
                rooms_occupied = occupied.mapped("room_id.id")
                if line.room_id.id in rooms_occupied:
                    raise ValidationError(
                        _(
                            "This room is occupied!, please, \
                        choice other room or change the reservation date"
                        )
                    )

    @api.onchange(
        "checkin",
        "checkout",
        "room_type_id",
        "discount",
        "board_service_room_id",
        "product_ids",
    )
    def onchange_dates(self):
        for line in self:
            if not line.checkin:
                line.checkin = line.folio_wizard_id.checkin
            if not line.checkout:
                line.checkout = line.folio_wizard_id.checkout

            start_date_utc_dt = fields.Date.from_string(line.checkin)
            end_date_utc_dt = fields.Date.from_string(line.checkout)

            if line.room_type_id:
                # First, compute room price
                pricelist_id = line.folio_wizard_id.pricelist_id.id
                nights = abs((end_date_utc_dt - start_date_utc_dt).days)
                res_price = 0
                for i in range(0, nights):
                    ndate = start_date_utc_dt + timedelta(days=i)
                    ndate_str = ndate.strftime(DEFAULT_SERVER_DATE_FORMAT)
                    product = line.room_type_id.product_id.with_context(
                        lang=line.partner_id.lang,
                        partner=line.partner_id.id,
                        quantity=1,
                        date=ndate_str,
                        pricelist=pricelist_id,
                        uom=line.room_type_id.product_id.uom_id.id,
                    )
                    res_price += product.price
                board_service = line.board_service_room_id
                # Second, compute BoardService price
                if board_service:
                    if board_service.price_type == "fixed":
                        board_price = board_service.amount * line.adults * nights
                        res_price += board_price
                    else:
                        res_price += (res_price * board_service.amount) * 0.01
                res_price = res_price - (res_price * line.discount) * 0.01
                # And compute products Room price
                for product in line.product_ids:
                    pricelist_id = line.folio_wizard_id.pricelist_id.id
                    product = product.with_context(
                        lang=line.folio_wizard_id.partner_id.lang,
                        partner=line.folio_wizard_id.partner_id.id,
                        quantity=1,
                        date=fields.Datetime.now(),
                        pricelist=pricelist_id,
                        uom=product.uom_id.id,
                    )
                    values = {
                        "pricelist_id": pricelist_id,
                        "product_id": product.id,
                        "product_qty": 1,
                    }
                    service_line = self.env["pms.service"].new(values)
                    vals = service_line.with_context(
                        {"default_folio_id": line.folio_wizard_id}
                    )._prepare_add_missing_fields(values)
                    if product.per_day or product.per_person:
                        checkin_dt = fields.Date.from_string(line.checkin)
                        checkout_dt = fields.Date.from_string(line.checkout)
                        nights = abs((checkout_dt - checkin_dt).days)
                        vals.update(
                            service_line.prepare_service_ids(
                                dfrom=line.checkin,
                                days=nights,
                                per_person=product.per_person,
                                persons=line.adults,
                                old_line_days=False,
                                consumed_on=product.consumed_on,
                            )
                        )
                    service_line.update(vals)
                    price_product = service_line.price_unit * (
                        1 - (line.discount or 0.0) * 0.01
                    )
                    pricelist = line.folio_wizard_id.pricelist_id
                    currency = pricelist.currency_id
                    taxes = service_line.tax_ids.compute_all(
                        price_product,
                        currency,
                        service_line.product_qty,
                        product=product,
                    )
                    # TODO Daily Limits
                    res_price += taxes["total_included"]
                line.price = res_price
            end_date_utc_dt -= timedelta(days=1)
            occupied = self.env["pms.reservation"].get_reservations(
                line.checkin, end_date_utc_dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
            )
            rooms_occupied = occupied.mapped("room_id.id")
            domain_rooms = [("id", "not in", rooms_occupied)]
            return {"domain": {"room_id": domain_rooms}}


class ServiceWizard(models.TransientModel):
    _name = "pms.service.wizard"
    _description = "Virtual Service for Groups"

    product_id = fields.Many2one("product.product", string="Service")
    name = fields.Char("Description")
    folio_wizard_id = fields.Many2one("pms.folio.wizard")
    discount = fields.Float("discount")
    price_unit = fields.Float(
        "Unit Price", required=True, digits=("Product Price"), default=0.0
    )
    price_total = fields.Float(
        compute="_compute_amount", string="Total", readonly=True, store=True
    )
    tax_ids = fields.Many2many(
        "account.tax",
        string="Taxes",
        domain=["|", ("active", "=", False), ("active", "=", True)],
    )
    product_uom_qty = fields.Float(
        string="Quantity",
        digits=("Product Unit of Measure"),
        required=True,
        default=1.0,
    )

    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            pricelist_id = self.folio_wizard_id.pricelist_id.id
            prod = self.product_id.with_context(
                lang=self.folio_wizard_id.partner_id.lang,
                partner=self.folio_wizard_id.partner_id.id,
                quantity=1,
                date=fields.Datetime.now(),
                pricelist=pricelist_id,
                uom=self.product_id.uom_id.id,
            )
            # TODO change pricelist for partner
            values = {"pricelist_id": pricelist_id, "product_id": prod.id}
            line = self.env["pms.service"].new(values)
            vals = line.with_context(
                {"default_folio_id": self.folio_wizard_id}
            )._prepare_add_missing_fields(values)
            self.update(vals)

    @api.depends("product_uom_qty", "discount", "price_unit", "tax_ids")
    def _compute_amount(self):
        """
        Compute the amounts of the service line.
        """
        for record in self:
            pricelist = record.folio_wizard_id.pricelist_id
            currency = pricelist.currency_id
            product = record.product_id
            price = record.price_unit * (1 - (record.discount or 0.0) * 0.01)
            taxes = record.tax_ids.compute_all(
                price, currency, record.product_uom_qty, product=product
            )
            record.update(
                {"price_total": taxes["total_included"],}
            )
