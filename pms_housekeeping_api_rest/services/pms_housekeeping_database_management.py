import subprocess
import os
import odoo.tools.config as config
from odoo import exceptions
from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component
import logging
import tempfile


_logger = logging.getLogger(__name__)

# Directorio para almacenar los snapshots. Asegúrate de que el usuario Odoo tenga permisos aquí.
SNAPSHOT_DIR = tempfile.gettempdir()

class PmsDatabaseManagement(Component):
    _inherit = "base.rest.service"
    _name = "pms.housekeeping.db_management.service"  # Nombre único para este servicio
    _usage = "db-management"
    _collection = "pms.housekeeping.services"

    @restapi.method(
        [
            (
                [
                    "/snapshot"
                ],
                "POST",
            )
        ],
        auth="jwt_api_pms_housekeeping",
    )
    def create_db_snapshot(self):
        """
        Crea un snapshot de la base de datos en formato custom.
        """
        db_name = self.env.cr.dbname
        db_user = config.get('db_user') or 'odoo'
        db_host = config.get('db_host') or 'localhost'
        db_port = config.get('db_port') or '5432'
        db_password = config.get('db_password')

        # Usaremos un archivo .dump para el snapshot
        snapshot_file = os.path.join(SNAPSHOT_DIR, "{}_snapshot.dump".format(db_name))
        env = os.environ.copy()
        if db_password:
            env['PGPASSWORD'] = db_password

        # Comando para crear el snapshot en formato custom
        cmd = [
            'pg_dump',
            '-U', db_user,
            '-h', db_host,
            '-p', str(db_port),
            '-Fc',       # Formato custom
            db_name,
            '-f', snapshot_file
        ]

        try:
            subprocess.run(cmd, env=env, check=True)
            _logger.info("Snapshot created successfully. %s", snapshot_file)
        except subprocess.CalledProcessError as e:
            raise exceptions.UserError("Error creating snapshot: {}".format(e))

        return {"status": "Snapshot created successfully", "file": snapshot_file}

    @restapi.method(
        [
            (
                ["/rollback"],
                "POST",
            )
        ],
        auth="jwt_api_pms_housekeeping",
    )
    def rollback_db_snapshot(self):
        db_name = self.env.cr.dbname
        db_user = config.get('db_user') or 'odoo'
        db_host = config.get('db_host') or 'localhost'
        db_port = config.get('db_port') or '5432'
        db_password = config.get('db_password')

        snapshot_file = os.path.join(SNAPSHOT_DIR, "{}_snapshot.dump".format(db_name))
        if not os.path.exists(snapshot_file):
            raise exceptions.UserError("No snapshot exists. Please take a snapshot first.")
        env = os.environ.copy()
        if db_password:
            env['PGPASSWORD'] = db_password
        cmd = [
            'pg_restore',
            '--clean',
            '--no-owner',
            '-U', db_user,
            '-h', db_host,
            '-p', str(db_port),
            '-d', db_name,
            snapshot_file
        ]

        try:
            self.env.cr.commit()
            _logger.info("Connection released, continuing with pg_restore...")
        except Exception as e:
            raise exceptions.UserError("Error releasing connection: %s", e)

        try:
            subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
            _logger.info("Rollback done successfully")
        except subprocess.CalledProcessError as e:
            raise exceptions.UserError("Error while doing rollback: {}".format(e))


        return {"status": "Rollback done successfully", "file": snapshot_file}
