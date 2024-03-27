from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PropertyWizard(models.TransientModel):
    _name = "property.wizard"
    _inherit = ["multi.step.wizard.mixin"]

    company_ids = fields.Many2many("res.company", string="Companies")
    company_name = fields.Char("Name")
    company_nif = fields.Char("NIF")
    company_logo = fields.Binary("Logo")
    company_address = fields.Text("Address")
    company_mail = fields.Char("Mail")
    company_web = fields.Char("Web")
    company_tlf = fields.Char("Phone")

    property_name = fields.Char("Name")
    property_logo = fields.Binary("Logo")
    property_address = fields.Text("Address")
    property_photo = fields.Binary("Photo")
    property_tlf = fields.Char("Phone")
    property_web = fields.Char("Web")
    property_lang = fields.Text("Languages")

    # room_type_ids = fields.One2many (comodel_name="pms.room.type",
    #     inverse_name="property_wizard_id",
    #     string="Room types",)

    def _get_available_companies(self):
        companies = self.env["res.company"].search([])
        company_list = [(company.id, company.name) for company in companies]
        return company_list

    selected_company = fields.Selection(
        selection="_get_available_companies", string="Select Company", required=True
    )
    selected_company_id = fields.Many2one("res.company", string="Selected Company")
    selected_property = fields.Many2one(
        "pms.property",
        string="Select Property",
        required=True,
        domain="[('company_id', '=', selected_company_id)]",
    )

    @api.onchange("selected_company_id")
    def _onchange_selected_company_id(self):
        if self.selected_company_id:
            domain = [("company_id", "=", self.selected_company_id.id)]
            return {"domain": {"selected_property": domain}}
        else:
            return {"domain": {"selected_property": []}}

    @api.model
    def _selection_state(self):
        return [
            ("start", "Start"),
            ("property", "Property"),
            ("rooms", "Rooms"),
            ("final", "Final"),
        ]

    @api.model
    def _default_project_id(self):
        return self.env.context.get("active_id")

    def state_exit_start(self):
        if not self.selected_company:
            raise ValidationError(_("Please select a company."))

        selected_company = self.env["res.company"].browse(int(self.selected_company))

        if self.company_name:
            selected_company.write({"name": self.company_name})
        if self.company_mail:
            selected_company.write({"phone": self.company_mail})

        self.state = "property"

    def state_exit_property(self):
        if not self.selected_property:
            raise ValidationError(_("Please select a property."))

        selected_property = self.env["pms.property"].browse(int(self.selected_property))
        if self.property_name:
            selected_property.write({"name": self.property_name})
        if self.property_mail:
            selected_property.write({"phone": self.property_mail})

        self.state = "rooms"
