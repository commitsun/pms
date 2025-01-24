from datetime import datetime, date, timedelta, timezone

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component

from odoo.odoo.exceptions import ValidationError
from odoo.odoo.tools.safe_eval import pytz
from ..pms_housekeeping_api_rest_utils import check_api_housekeeping_access




class PmsHousekeepingTask(Component):
    _inherit = "base.rest.service"
    _name = "pms.housekeeping.task"
    _usage = "tasks"
    _collection = "pms.housekeeping.services"

    @restapi.method(
        [
            (
                [
                    "/",
                ],
                "GET",
            )
        ],
        input_param=Datamodel("pms.housekeeping.task.input", is_list=False),
        output_param=Datamodel("pms.housekeeping.task.info", is_list=True),
        auth="jwt_api_pms_housekeeping",
    )
    def get_tasks(self, task_search):
        if check_api_housekeeping_access(self.env.user, task_search.pmsPropertyUuid):
            domain = []
            tasks = []
            if task_search.pmsPropertyUuid:
                pms_property = self.env["pms.property"].sudo().search([("housekeeping_uuid", "=", task_search.pmsPropertyUuid)])
                rooms = self.env["pms.room"].sudo().search([("pms_property_id", "=", pms_property.id)])
                domain.append(("room_id", "in", rooms.ids))
            if task_search.employeeUuid:
                employee = self.env["hr.employee"].sudo().search(
                    [("housekeeping_uuid", "=", task_search.employeeUuid)]
                )
                domain += [
                    "|",
                    ("housekeeper_ids", "in", [employee.id]),
                    ("housekeeper_ids", "=", False),
                ]
            if task_search.taskTypeUuid:
                task_types = self.env["pms.housekeeping.task.type"].sudo().search([("housekeeping_uuid", "=", task_search.taskTypeUuid)])
                domain.append(("task_type_id", "in", task_types.ids))
            if task_search.name:
                domain.append(("name", "ilike", task_search.name))
            if task_search.states:
                domain.append(("state", "in", task_search.states))
            if task_search.date:
                task_date = task_search.date.replace('Z', '+00:00')
                domain.append(("task_date", "=", task_date))
            if task_search.dateFrom or task_search.dateTo:
                if task_search.dateFrom:
                    date_from = datetime.fromisoformat(task_search.dateFrom.replace('Z', '+00:00'))
                    domain.append(("task_date", ">=", date_from))
                if task_search.dateTo:
                    date_to = datetime.fromisoformat(task_search.dateTo.replace('Z', '+00:00'))
                    domain.append(("task_date", "<=", date_to))
            if task_search.completedDateTime:
                task_completed_datetime = datetime.fromisoformat(task_search.completedDateTime.replace('Z', '+00:00'))
                start_of_day = task_completed_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_day = start_of_day + timedelta(days=1, microseconds=-1)

                domain += [
                    ("task_completed_datetime", ">=", start_of_day),
                    ("task_completed_datetime", "<=", end_of_day)
                ]
            if task_search.roomUuid:
                domain.append(("room_id", "=", task_search.roomUuid))
            limit = task_search.limit if task_search.limit else 100
            offset = task_search.offset if task_search.offset else 0
            order = task_search.order if task_search.order else "asc"
            sort = task_search.sort if task_search.sort else "id"
            PmsHousekeepingTask = self.env.datamodels["pms.housekeeping.task.info"]
            tasks_sudo = self.env["pms.housekeeping.task"].sudo().search(domain, limit=limit, offset=offset, order=sort + " " + order)
            for task_sudo in tasks_sudo:
                task_date = datetime.combine(task_sudo.task_date, datetime.min.time()).isoformat()
                task_completed_datetime = None
                if task_sudo.task_completed_datetime:
                    task_completed_datetime = str(datetime.fromisoformat(str(task_sudo.task_completed_datetime)))
                tasks.append(
                    PmsHousekeepingTask(
                        uuid=task_sudo.housekeeping_uuid,
                        name=task_sudo.name,
                        description=task_sudo.task_type_id.description if task_sudo.task_type_id.description else "",
                        taskTypeUuid=task_sudo.task_type_id.housekeeping_uuid,
                        # employeeId=user.id,
                        state=task_sudo.state,
                        date=task_date if task_sudo.task_date else None,
                        completedDateTime=task_completed_datetime,
                        priority=task_sudo.priority,
                        roomUuid=task_sudo.room_id.housekeeping_uuid,
                        reservationUuid=task_sudo.reservation_id.housekeeping_uuid if task_sudo.reservation_id else None,
                        annotations=task_sudo.cleaning_comments if task_sudo.cleaning_comments else "",
                        pmsPropertyUuid=task_sudo.room_id.pms_property_id.housekeeping_uuid if task_sudo.room_id else None,
                    )
                )
            return tasks

    @restapi.method(
        [
            (
                [
                    "/<string:task_uuid>",
                ],
                "GET",
            )
        ],
        output_param=Datamodel("pms.housekeeping.task.info", is_list=False),
        input_param=Datamodel("pms.housekeeping.task.input", is_list=False),
        auth="jwt_api_pms_housekeeping",
    )
    def get_task(self, task_uuid, task_search):
        if check_api_housekeeping_access(self.env.user, task_search.pmsPropertyUuid):
            user = self.env.user
            PmsHousekeepingTask = self.env.datamodels["pms.housekeeping.task.info"]
            task_sudo = self.env["pms.housekeeping.task"].sudo().search([("housekeeping_uuid", "=", task_uuid)])
            task_date = datetime.combine(task_sudo.task_date, datetime.min.time()).isoformat()
            task_completed_datetime = None
            if task_sudo.task_completed_datetime:
                task_completed_datetime = datetime.combine(task_sudo.task_completed_datetime, datetime.min.time()).isoformat()

            return PmsHousekeepingTask(
                uuid=task_sudo.housekeeping_uuid,
                name=task_sudo.name,
                description=task_sudo.cleaning_comments or "",
                taskTypeUuid=task_sudo.task_type_id.housekeeping_uuid,
                employeeUuid=user.housekeeping_uuid if user else None,
                state=task_sudo.state,
                date=task_date if task_sudo.task_date else None,
                completedDateTime=task_completed_datetime,
                priority=task_sudo.priority,
                roomUuid=task_sudo.room_id.housekeeping_uuid,
                reservationUuid=task_sudo.reservation_id.housekeeping_uuid if task_sudo.reservation_id else None,
                annotations=task_sudo.cleaning_comments if task_sudo.cleaning_comments else "",
                pmsPropertyUuid=task_sudo.room_id.pms_property_id.housekeeping_uuid if task_sudo.room_id else None,

            )

    @restapi.method(
        [
            (
                [
                    "/p/<string:task_uuid>",
                ],
                "PATCH",
            )
        ],
        input_param=Datamodel("pms.housekeeping.task.info", is_list=False),
        auth="jwt_api_pms_housekeeping",
    )
    def update_task(self, task_uuid, task_data):
        if check_api_housekeeping_access(self.env.user, task_data.pmsPropertyUuid):
            task_sudo = self.env["pms.housekeeping.task"].sudo().search([("housekeeping_uuid", "=", task_uuid)])

            pms_property = self.env["pms.property"].sudo().search([
                ("housekeeping_uuid", "=", task_data.pmsPropertyUuid)
            ], limit=1)

            if not pms_property or not pms_property.tz:
                raise ValidationError("Property timezone not set")

            property_tz = pytz.timezone(pms_property.tz)

            vals = {}
            if task_data.state:
                vals["state"] = task_data.state

            if task_data.completedDateTime:
                completed_datetime_utc = datetime.fromisoformat(task_data.completedDateTime.replace('Z', '+00:00'))
                completed_datetime_property_tz = completed_datetime_utc.astimezone(property_tz)
                vals["task_completed_datetime"] = completed_datetime_property_tz.strftime('%Y-%m-%d %H:%M:%S')

            if task_data.annotations:
                vals["cleaning_comments"] = task_data.annotations
            task_sudo.write(vals)

    @restapi.method(
        [
            (
                [
                    "/count",
                ],
                "GET",
            )
        ],
        input_param=Datamodel("pms.housekeeping.task.input", is_list=False),
        auth="jwt_api_pms_housekeeping",
    )
    def get_count_tasks(self, task_search):
        if check_api_housekeeping_access(self.env.user, task_search.pmsPropertyUuid):
            domain = []
            if task_search.pmsPropertyUuid:
                pms_property = self.env["pms.property"].sudo().search(
                    [("housekeeping_uuid", "=", task_search.pmsPropertyUuid)])
                rooms = self.env["pms.room"].sudo().search([("pms_property_id", "=", pms_property.id)])
                domain.append(("room_id", "in", rooms.ids))
            if task_search.employeeUuid:
                employee = self.env["hr.employee"].sudo().search(
                    [("housekeeping_uuid", "=", task_search.employeeUuid)]
                )
                domain += [
                    "|",
                    ("housekeeper_ids", "in", [employee.id]),
                    ("housekeeper_ids", "=", False),
                ]
            if task_search.taskTypeUuid:
                domain.append(("housekeeping_uuid", "=", task_search.taskTypeUuid))
            if task_search.name:
                domain.append(("name", "ilike", task_search.name))
            if task_search.states:
                domain.append(("state", "in", task_search.states))
            if task_search.date:
                task_date = task_search.date.replace('Z', '+00:00')
                domain.append(("task_date", "=", task_date))
            if task_search.dateFrom or task_search.dateTo:
                if task_search.dateFrom:
                    date_from = datetime.fromisoformat(task_search.dateFrom.replace('Z', '+00:00'))
                    domain.append(("task_date", ">=", date_from))
                if task_search.dateTo:
                    date_to = datetime.fromisoformat(task_search.dateTo.replace('Z', '+00:00'))
                    domain.append(("task_date", "<=", date_to))
            if task_search.completedDateTime:
                task_completed_datetime = task_search.completedDateTime.replace('Z', '+00:00')
                domain.append(("task_completed_datetime", "=", task_completed_datetime))
            return self.env["pms.housekeeping.task"].sudo().search_count(domain)
