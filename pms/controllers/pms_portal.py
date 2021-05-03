from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class PortalFolio(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        partner = request.env.user.partner_id
        values = super()._prepare_home_portal_values(counters)
        Folio = request.env["pms.folio"]
        if "folio_count" in counters:
            values["folio_count"] = (
                Folio.search_count(
                    [
                        ("partner_id", "=", partner.id),
                    ]
                )
                if Folio.check_access_rights("read", raise_exception=False)
                else 0
            )
        return values

    def _folio_get_page_view_values(self, folio, access_token, **kwargs):
        values = {"folio": folio, "token": access_token}
        return self._get_page_view_values(
            folio, access_token, values, "my_folios_history", False, **kwargs
        )

    @http.route(
        ["/my/folios", "/my/folios/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_folios(
        self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw
    ):
        partner = request.env.user.partner_id
        values = self._prepare_portal_layout_values()
        PmsFolio = request.env["pms.folio"]
        values["folios"] = PmsFolio.search(
            [
                ("partner_id", "child_of", partner.id),
            ]
        )
        domain = [
            ("partner_id", "child_of", partner.id),
        ]
        searchbar_sortings = {
            "date": {"label": _("Order Date"), "folio": "date_order desc"},
            "name": {"label": _("Reference"), "folio": "name"},
            "stage": {"label": _("Stage"), "folio": "state"},
        }
        if not sortby:
            sortby = "date"
        sort_order = searchbar_sortings[sortby]["folio"]

        if date_begin and date_end:
            domain += [
                ("create_date", ">", date_begin),
                ("create_date", "<=", date_end),
            ]
        folio_count = PmsFolio.search_count(domain)
        pager = portal_pager(
            url="/my/folios",
            url_args={"date_begin": date_begin, "date_end": date_end, "sortby": sortby},
            total=folio_count,
            page=page,
            step=self._items_per_page,
        )
        folios = PmsFolio.search(
            domain, order=sort_order, limit=self._items_per_page, offset=pager["offset"]
        )
        request.session["my_folios_history"] = folios.ids[:100]
        values.update(
            {
                "date": date_begin,
                "folios": folios.sudo(),
                "page_name": "folios",
                "pager": pager,
                "default_url": "/my/folios",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render("pms.portal_my_folio", values)

    @http.route(["/my/folios/<int:folio_id>"], type="http", auth="user", website=True)
    def portal_my_folio_detail(
        self, folio_id, access_token=None, report_type=None, download=False, **kw
    ):
        try:
            folio_sudo = self._document_check_access(
                "pms.folio",
                folio_id,
                access_token=access_token,
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        if report_type in ("html", "pdf", "text"):
            return self._show_report(
                model=folio_sudo,
                report_type=report_type,
                report_ref="pms.action_report_folio",
                download=download,
            )
        values = self._folio_get_page_view_values(folio_sudo, access_token, **kw)
        return request.render("pms.folio_portal_template", values)

    @http.route(
        ["/my/folios/<int:folio_id>/precheckin"], type="http", auth="user", website=True
    )
    def portal_my_folio_precheckin(
        self, folio_id, access_token=None, report_type=None, download=False, **kw
    ):
        try:
            folio_sudo = self._document_check_access(
                "pms.folio",
                folio_id,
                access_token=access_token,
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        values = self._folio_get_page_view_values(folio_sudo, access_token, **kw)
        values.update({"no_breadcrumbs": True})
        return request.render("pms.portal_my_folio_precheckin", values)


class PortalReservation(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        partner = request.env.user.partner_id
        values = super()._prepare_home_portal_values(counters)
        Reservation = request.env["pms.reservation"]
        if "reservation_count" in counters:
            values["reservation_count"] = (
                Reservation.search_count(
                    [
                        ("partner_id", "=", partner.id),
                    ]
                )
                if Reservation.check_access_rights("read", raise_exception=False)
                else 0
            )
        return values

    def _reservation_get_page_view_values(self, reservation, access_token, **kwargs):
        values = {"reservation": reservation, "token": access_token}
        return self._get_page_view_values(
            reservation,
            access_token,
            values,
            "my_reservations_history",
            False,
            **kwargs
        )

    @http.route(
        ["/my/reservations", "/my/reservations/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_reservations(
        self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw
    ):
        partner = request.env.user.partner_id
        values = self._prepare_portal_layout_values()
        Reservation = request.env["pms.reservation"]
        values["reservations"] = Reservation.search(
            [
                ("partner_id", "child_of", partner.id),
            ]
        )
        domain = [
            ("partner_id", "child_of", partner.id),
        ]
        if date_begin and date_end:
            domain += [
                ("create_date", ">", date_begin),
                ("create_date", "<=", date_end),
            ]
        reservation_count = Reservation.search_count(domain)
        pager = portal_pager(
            url="/my/reservations",
            url_args={"date_begin": date_begin, "date_end": date_end},
            total=reservation_count,
            page=page,
            step=self._items_per_page,
        )
        reservations = Reservation.search(
            domain, limit=self._items_per_page, offset=pager["offset"]
        )
        folios_dict = {}
        for reservation in reservations:
            folio = reservation.folio_id
            folios_dict[folio] = ""

        request.session["my_reservations_history"] = reservations.ids[:100]
        values.update(
            {
                "date": date_begin,
                "reservations": reservations.sudo(),
                "page_name": "reservations",
                "pager": pager,
                "default_url": "/my/reservations",
                "folios_dict": folios_dict,
                "partner": partner,
            }
        )
        return request.render("pms.portal_my_reservation", values)

    @http.route(
        ["/my/reservations/<int:reservation_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_reservation_detail(self, reservation_id, access_token=None, **kw):
        try:
            reservation_sudo = self._document_check_access(
                "pms.reservation",
                reservation_id,
                access_token=access_token,
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        # for attachment in reservation_sudo.attachment_ids:
        #     attachment.generate_access_token()
        values = self._reservation_get_page_view_values(
            reservation_sudo, access_token, **kw
        )
        return request.render("pms.portal_my_reservation_detail", values)

    @http.route(
        ["/my/reservations/<int:reservation_id>/precheckin"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_reservation_precheckin(
        self, reservation_id, access_token=None, report_type=None, download=False, **kw
    ):
        try:
            reservation_sudo = self._document_check_access(
                "pms.reservation",
                reservation_id,
                access_token=access_token,
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        values = self._reservation_get_page_view_values(
            reservation_sudo, access_token, **kw
        )
        values.update({"no_breadcrumbs": True})
        return request.render("pms.portal_my_reservation_precheckin", values)


class PortalPrecheckin(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        partner = request.env.user.partner_id
        values = super()._prepare_home_portal_values(counters)
        Reservation = request.env["pms.reservation"].search(
            [("partner_id", "=", partner.id)]
        )
        if "checkin_count" in counters:
            checkin_partner_count = len(Reservation.checkin_partner_ids)
            values["checkin_count"] = (
                checkin_partner_count
                if Reservation.check_access_rights("read", raise_exception=False)
                else 0
            )
        return values

    def _precheckin_get_page_view_values(self, checkin_partner, access_token, **kwargs):
        values = {"checkin_partner": checkin_partner, "token": access_token}
        return self._get_page_view_values(
            checkin_partner,
            access_token,
            values,
            "my_precheckins_history",
            False,
            **kwargs
        )

    @http.route(
        ["/my/precheckin/<int:checkin_partner_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_precheckin_detail(self, checkin_partner_id, access_token=None, **kw):
        try:
            checkin_sudo = self._document_check_access(
                "pms.checkin.partner",
                checkin_partner_id,
                access_token=access_token,
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        values = self._precheckin_get_page_view_values(checkin_sudo, access_token, **kw)
        values.update({"no_breadcrumbs": True})
        return request.render("pms.portal_my_precheckin_detail", values)

    @http.route(["/my/precheckin"], type="http", auth="user", website=True, csrf=False)
    def portal_precheckin_submit(self, **kw):
        checkin_partner = request.env["pms.checkin.partner"].browse(int(kw.get("id")))
        if not checkin_partner.partner_id:
            ResPartner = request.env["res.partner"]
            res_partner = ResPartner.create(kw)
            kw.update(
                {
                    "partner_id": res_partner.id,
                }
            )
        else:
            res_partner = checkin_partner.partner_id
            res_partner.write(kw)
        checkin_partner.write(kw)

    @http.route(
        ["/my/precheckin/folio_reservation"],
        type="http",
        auth="user",
        website=False,
        csrf=True,
    )
    def portal_precheckin_folio_submit(self, **kw):
        counter = 1
        if kw.get("folio_id"):
            folio = request.env["pms.folio"].browse(int(kw.get("folio_id")))
            checkin_partners = len(folio.checkin_partner_ids)
        elif kw.get("reservation_id"):
            reservation = request.env["pms.reservation"].browse(
                int(kw.get("reservation_id"))
            )
            checkin_partners = len(reservation.checkin_partner_ids)
        for _checkin in range(checkin_partners):
            values = {
                "firstname": kw.get("firstname-" + str(counter)),
                "lastname": kw.get("lastname-" + str(counter)),
                "lastname2": kw.get("lastname2-" + str(counter)),
                "gender": kw.get("gender-" + str(counter)),
                "birthdate_date": kw.get("birthdate_date-" + str(counter))
                if kw.get("birthdate_date-" + str(counter))
                else False,
                "document_type": kw.get("document_type-" + str(counter)),
                "document_number": kw.get("document_number-" + str(counter)),
                "document_expedition_date": kw.get(
                    "document_expedition_date-" + str(counter)
                )
                if kw.get("document_expedition_date-" + str(counter))
                else False,
                "mobile": kw.get("mobile-" + str(counter)),
                "email": kw.get("email-" + str(counter)),
            }
            checkin_partner_id = int(kw.get("id-" + str(counter)))
            checkin_partner = request.env["pms.checkin.partner"].browse(
                checkin_partner_id
            )
            lastname = True if kw.get("lastname-" + str(counter)) else False
            firstname = True if kw.get("firstname-" + str(counter)) else False
            lastname2 = True if kw.get("lastname2-" + str(counter)) else False
            if not checkin_partner.partner_id and (lastname or firstname or lastname2):
                ResPartner = request.env["res.partner"]
                res_partner = ResPartner.create(values)
                values.update(
                    {
                        "partner_id": res_partner.id,
                    }
                )
            elif checkin_partner.partner_id:
                res_partner = checkin_partner.partner_id
                res_partner.write(values)
            checkin_partner.write(values)
            counter = counter + 1
