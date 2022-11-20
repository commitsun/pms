from odoo import _, fields
from odoo.exceptions import UserError

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component


class PmsInvoiceService(Component):
    _inherit = "base.rest.service"
    _name = "pms.invoice.service"
    _usage = "invoices"
    _collection = "pms.services"

    @restapi.method(
        [
            (
                [
                    "/p/<int:invoice_id>",
                ],
                "PATCH",
            )
        ],
        input_param=Datamodel("pms.invoice.info"),
        auth="jwt_api_pms",
    )
    # flake8: noqa: C901
    def update_invoice(self, invoice_id, pms_invoice_info):
        invoice = self.env["account.move"].browse(invoice_id)
        if invoice.move_type in ["in_refund", "out_refund"]:
            raise UserError(_("You can't update a refund invoice"))
        if invoice.payment_state == "reversed":
            raise UserError(_("You can't update a reversed invoice"))
        new_vals = {}
        if (
            pms_invoice_info.partnerId
            and pms_invoice_info.partnerId != invoice.partner_id.id
        ):
            new_vals["partner_id"] = pms_invoice_info.partnerId

        if pms_invoice_info.date:
            invoice_date_info = fields.Date.from_string(pms_invoice_info.date)
            if invoice_date_info != invoice.invoice_date:
                new_vals["invoice_date"] = invoice_date_info

        # If invoice lines are updated, we expect that all lines will be
        # send to service, the lines that are not sent we assume that
        # they have been eliminated
        if pms_invoice_info.moveLines is not None:
            cmd_invoice_lines = self._get_invoice_lines_commands(
                invoice, pms_invoice_info
            )
            if cmd_invoice_lines:
                new_vals["invoice_line_ids"] = cmd_invoice_lines
        new_invoice = False
        if new_vals:
            # Update Invoice
            # When modifying an invoice, depending on the company's configuration,
            # and the invoice stateit will be modified directly or a reverse
            # of the current invoice will be created to later create a new one
            # with the updated data.
            # TODO: to create core pms correct_invoice_policy field
            # if invoice.state != "draft" and company.corrective_invoice_policy == "strict":
            if invoice.state == "posted":
                # invoice create refund
                new_invoice = invoice.copy()
                cmd_new_invoice_lines = []
                for item in cmd_invoice_lines:
                    # susbstituted in new_vals reversed invoice line id by new invoice line id
                    if item[0] == 0:
                        cmd_new_invoice_lines.append(item)
                    else:
                        folio_line_ids = self.env["folio.sale.line"].browse(
                            self.env["account.move.line"]
                            .browse(item[1])
                            .folio_line_ids.ids
                        )
                        new_id = new_invoice.invoice_line_ids.filtered(
                            lambda l: l.folio_line_ids == folio_line_ids
                        ).id
                        if item[0] == 2:
                            # delete
                            cmd_new_invoice_lines.append((2, new_id))
                        else:
                            # update
                            cmd_new_invoice_lines.append((1, new_id, item[2]))
                if cmd_new_invoice_lines:
                    new_vals["invoice_line_ids"] = cmd_new_invoice_lines
                invoice._reverse_moves(cancel=True)
                # Update Journal by partner if necessary (simplified invoice -> normal invoice)
                new_vals["journal_id"] = (
                    invoice.pms_property_id._get_folio_default_journal(
                        new_vals.get("partner_id", invoice.partner_id.id)
                    ).id,
                )
                new_invoice.write(new_vals)
                new_invoice.sudo().action_post()
            else:
                new_invoice = self._direct_move_update(invoice, new_vals)
        invoice_to_update = new_invoice or invoice
        if pms_invoice_info.narration is not None:
            invoice_to_update.write({"narration": pms_invoice_info.narration})
        if invoice_to_update.state == "draft" and pms_invoice_info.state == "confirm":
            invoice_to_update.action_post()
        return invoice.id

    def _direct_move_update(self, invoice, new_vals):
        previus_state = invoice.state
        if previus_state == "posted":
            invoice.button_draft()
        if new_vals:
            invoice.write(new_vals)
        if previus_state == "posted":
            invoice.action_post()
        return invoice

    @restapi.method(
        [
            (
                [
                    "/",
                ],
                "POST",
            )
        ],
        input_param=Datamodel("pms.invoice.info"),
        auth="jwt_api_pms",
    )
    def create_invoice(self, pms_invoice_info):
        if pms_invoice_info.originDownPaymentId:
            if not pms_invoice_info.partnerId:
                raise UserError(_("For manual invoice, partner is required"))
            payment = self.env["account.payment"].browse(
                pms_invoice_info.originDownPaymentId
            )
            self.env["account.payment"]._create_downpayment_invoice(
                payment=payment,
                partner_id=pms_invoice_info.partnerId,
            )

    @restapi.method(
        [
            (
                [
                    "/<int:invoice_id>/send-mail",
                ],
                "POST",
            )
        ],
        input_param=Datamodel("pms.mail.info"),
        auth="jwt_api_pms",
    )
    def send_invoice_mail(self, invoice_id, pms_mail_info):
        invoice = self.env["account.move"].browse(invoice_id)
        recipients = pms_mail_info.emailAddresses
        template = self.env.ref(
            "account.email_template_edi_invoice", raise_if_not_found=False
        )
        email_values = {
            "email_to": ",".join(recipients) if recipients else False,
            "email_from": invoice.pms_property_id.email
            if invoice.pms_property_id.email
            else False,
            "subject": pms_mail_info.subject,
            "body_html": pms_mail_info.bodyMail,
            "partner_ids": pms_mail_info.partnerIds
            if pms_mail_info.partnerIds
            else False,
            "recipient_ids": pms_mail_info.partnerIds
            if pms_mail_info.partnerIds
            else False,
            "auto_delete": False,
        }
        template.send_mail(invoice.id, force_send=True, email_values=email_values)
        return True

    def _get_invoice_lines_commands(self, invoice, pms_invoice_info):
        cmd_invoice_lines = []
        for line in invoice.invoice_line_ids:
            line_info = [
                item for item in pms_invoice_info.moveLines if item.id == line.id
            ]
            if line_info:
                line_info = line_info[0]
                line_values = {}
                if line_info.name and line_info.name != line.name:
                    line_values["name"] = line_info.name
                if line_info.quantity and line_info.quantity != line.quantity:
                    line_values["quantity"] = line_info.quantity
                if line_values:
                    cmd_invoice_lines.append((1, line.id, line_values))
            else:
                cmd_invoice_lines.append((2, line.id))
        # Get the new lines to add in invoice
        newInvoiceLinesInfo = list(
            filter(lambda item: not item.id, pms_invoice_info.moveLines)
        )
        if newInvoiceLinesInfo:
            partner = (
                self.env["res.partner"].browse(pms_invoice_info.partnerId)
                if pms_invoice_info.partnerId
                else invoice.partner_id
            )
            folios = self.env["pms.folio"].browse(
                list(
                    {
                        self.env["folio.sale.line"].browse(line.saleLineId).folio_id.id
                        for line in list(
                            filter(
                                lambda item: item.name,
                                pms_invoice_info.moveLines,
                            )
                        )
                    }
                )
            )
            new_invoice_lines = [
                item["invoice_line_ids"]
                for item in folios.get_invoice_vals_list(
                    lines_to_invoice={
                        newInvoiceLinesInfo[i]
                        .saleLineId: newInvoiceLinesInfo[i]
                        .quantity
                        for i in range(0, len(newInvoiceLinesInfo))
                    },
                    partner_invoice_id=partner.id,
                )
            ][0]
            # Update name of new invoice lines
            for item in new_invoice_lines:
                item[2]["name"] = [
                    line.name
                    for line in newInvoiceLinesInfo
                    if line.saleLineId == item[2]["folio_line_ids"][0][2]
                ][0]
            cmd_invoice_lines.extend(new_invoice_lines)
        return cmd_invoice_lines
