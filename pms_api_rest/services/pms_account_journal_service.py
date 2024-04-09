from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component
from odoo.exceptions import MissingError


class PmsAccountJournalService(Component):
    _inherit = "base.rest.service"
    _name = "pms.account.journal.service"
    _usage = "account-journals"
    _collection = "pms.services"

    @restapi.method(
        [
            (
                [
                    "/<int:pms_property_id>",
                ],
                "GET",
            )
        ],
        output_param=Datamodel("pms.account.journal.info", is_list=True),
        auth="jwt_api_pms",
    )
    def get_method_payments(self, pms_property_id):
        pms_property = self.env["pms.property"].search(
            [("id", "=", pms_property_id)],
        )
        PmsAccountJournalInfo = self.env.datamodels["pms.account.journal.info"]
        result_account_journals = []
        if not pms_property:
            raise MissingError("Property not found")
        else:
            for payment_method in pms_property._get_payment_methods(
                automatic_included=True
            ):
                # REVIEW: avoid send to app generic company journals
                if not payment_method.pms_property_ids:
                    continue
                result_account_journals.append(
                    PmsAccountJournalInfo(
                        id=payment_method.id,
                        name=payment_method.name,
                        type=payment_method.type,
                        allowedPayments=payment_method.allowed_pms_payments,
                    )
                )

        return result_account_journals
