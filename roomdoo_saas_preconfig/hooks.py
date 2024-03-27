import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(cr, _):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})

        # Importar geonames
        wizard_geonames = env["city.zip.geonames.import"].create({})
        wizard_geonames.run_import()
        _logger.info("Geonames data import completed successfully")

        # Importar ldatos bancarios
        wizard = env["l10n.es.partner.import.wizard"].create({})
        wizard.execute()

        # Eliminar los registros de digest.tip y digest.email
        env["digest.tip"].search([]).unlink()

        env["digest.email"].search([]).unlink()
