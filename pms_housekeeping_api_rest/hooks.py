from odoo import SUPERUSER_ID
from odoo.api import Environment
import uuid


def post_init_hook(cr, registry):
    with Environment.manage():
        env = Environment(cr, SUPERUSER_ID, {})
        users = env["res.users"].with_context(active_test=False).search([("housekeeping_uuid", "=", False)])
        for user in users:
            user.housekeeping_uuid = str(uuid.uuid4())
        employees = env["hr.employee"].with_context(active_test=False).search([("housekeeping_uuid", "=", False)])
        for employee in employees:
            employee.housekeeping_uuid = str(uuid.uuid4())
        housekeeping_tasks = env["pms.housekeeping.task"].with_context(active_test=False).search(
            [("housekeeping_uuid", "=", False)]
        )
        for housekeeping_task in housekeeping_tasks:
            housekeeping_task.housekeeping_uuid = str(uuid.uuid4())

        housekeeping_task_types = env["pms.housekeeping.task.type"].with_context(active_test=False).search(
            [("housekeeping_uuid", "=", False)]
        )
        for housekeeping_task_type in housekeeping_task_types:
            housekeeping_task_type.housekeeping_uuid = str(uuid.uuid4())
        properties = env["pms.property"].with_context(active_test=False).search([("housekeeping_uuid", "=", False)])
        for property in properties:
            property.housekeeping_uuid = str(uuid.uuid4())
        rooms = env["pms.room"].with_context(active_test=False).search([("housekeeping_uuid", "=", False)])
        for room in rooms:
            room.housekeeping_uuid = str(uuid.uuid4())
        reservations = env["pms.reservation"].with_context(active_test=False).search([("housekeeping_uuid", "=", False)])
        for reservation in reservations:
            reservation.housekeeping_uuid = str(uuid.uuid4())
