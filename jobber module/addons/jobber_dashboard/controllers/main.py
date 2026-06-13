from datetime import datetime, time, timedelta

import pytz

from odoo import fields, http
from odoo.http import request


class JobberDashboardController(http.Controller):
    @http.route("/jobber_dashboard/data", type="json", auth="user")
    def dashboard_data(self):
        env = request.env
        user = env.user
        now_utc = pytz.utc.localize(fields.Datetime.now())
        user_tz = pytz.timezone(user.tz or "UTC")
        now_local = now_utc.astimezone(user_tz)
        today = now_local.date()
        today_start = user_tz.localize(datetime.combine(today, time.min)).astimezone(pytz.utc).replace(tzinfo=None)
        tomorrow_start = user_tz.localize(datetime.combine(today + timedelta(days=1), time.min)).astimezone(pytz.utc).replace(tzinfo=None)

        lead_domain = [("type", "=", "lead"), ("active", "=", True), ("stage_id.is_won", "=", False)]
        quotation_domain = [("state", "in", ["sent", "sale"])]
        task_domain = [
            ("active", "=", True),
            "|",
            ("date_deadline", "<", fields.Date.to_string(today)),
            ("stage_id.fold", "=", False),
        ]
        invoice_domain = [
            ("move_type", "=", "out_invoice"),
            ("state", "=", "posted"),
            ("payment_state", "in", ["not_paid", "partial"]),
        ]
        overdue_invoice_domain = invoice_domain + [("invoice_date_due", "<", fields.Date.to_string(today))]
        late_task_domain = [
            ("active", "=", True),
            ("date_deadline", "<", fields.Date.to_string(today)),
            ("stage_id.fold", "=", False),
        ]
        upcoming_task_domain = [
            ("active", "=", True),
            ("date_deadline", ">=", fields.Date.to_string(today)),
            ("stage_id.fold", "=", False),
        ]
        appointment_today_domain = [
            ("start", ">=", fields.Datetime.to_string(today_start)),
            ("start", "<", fields.Datetime.to_string(tomorrow_start)),
        ]
        upcoming_schedule_domain = [
            ("start", ">=", fields.Datetime.to_string(today_start)),
        ]

        appointments = env["calendar.event"].search(appointment_today_domain)
        now_naive = now_utc.replace(tzinfo=None)
        active_appointments = appointments.filtered(lambda event: event.start and event.stop and event.start <= now_naive <= event.stop)
        completed_appointments = appointments.filtered(lambda event: event.stop and event.stop < now_utc.replace(tzinfo=None))
        remaining_appointments = appointments.filtered(lambda event: event.start and event.start > now_utc.replace(tzinfo=None))
        overdue_appointments = appointments.filtered(
            lambda event: event.start and event.stop and event.stop < now_naive and event.start.date() == today
        )
        upcoming_schedule_events = env["calendar.event"].search(upcoming_schedule_domain, order="start asc", limit=5)

        receivable_moves = env["account.move"].search(invoice_domain)
        revenue_domain = [
            ("move_type", "=", "out_invoice"),
            ("state", "=", "posted"),
            ("invoice_date", ">=", fields.Date.to_string(today.replace(day=1))),
        ]
        revenue_this_month = sum(env["account.move"].search(revenue_domain).mapped("amount_untaxed_signed"))

        def money(amount):
            return self._format_money(env.company.currency_id, amount)

        hour = now_local.hour
        if 5 <= hour <= 11:
            day_part = "morning"
        elif 12 <= hour <= 16:
            day_part = "afternoon"
        elif 17 <= hour <= 20:
            day_part = "evening"
        else:
            day_part = "night"

        actions = {
            "home": env.ref("jobber_dashboard.action_jobber_dashboard").id,
            "clients": env.ref("jobber_dashboard.action_jobber_clients").id,
            "leads": env.ref("jobber_dashboard.action_jobber_leads").id,
            "quotations": env.ref("jobber_dashboard.action_jobber_quotations").id,
            "tasks": env.ref("jobber_dashboard.action_jobber_tasks").id,
            "invoices": env.ref("jobber_dashboard.action_jobber_invoices").id,
            "schedule": env.ref("jobber_dashboard.action_jobber_schedule").id,
        }
        menus = {
            "home": env.ref("jobber_dashboard.menu_jobber_service_crm_home").id,
            "clients": env.ref("jobber_dashboard.menu_jobber_service_crm_clients").id,
            "leads": env.ref("jobber_dashboard.menu_jobber_service_crm_leads").id,
            "quotations": env.ref("jobber_dashboard.menu_jobber_service_crm_quotes").id,
            "tasks": env.ref("jobber_dashboard.menu_jobber_service_crm_tasks").id,
            "invoices": env.ref("jobber_dashboard.menu_jobber_service_crm_invoices").id,
            "schedule": env.ref("jobber_dashboard.menu_jobber_service_crm_schedule").id,
        }

        return {
            "todayLabel": now_local.strftime("%A, %B %d"),
            "greeting": f"Good {day_part}, {user.name}",
            "actions": actions,
            "menus": menus,
            "workflow": {
                "leads": {
                    "count": env["crm.lead"].search_count(lead_domain),
                    "sub": "Open lead opportunities",
                    "action": actions["leads"],
                },
                "quotations": {
                    "count": env["sale.order"].search_count(quotation_domain),
                    "sub": "Sent or approved quotations",
                    "action": actions["quotations"],
                },
                "tasks": {
                    "count": env["project.task"].search_count(task_domain),
                    "sub": "Open or late tasks",
                    "action": actions["tasks"],
                },
                "invoices": {
                    "count": env["account.move"].search_count(invoice_domain),
                    "sub": "Awaiting payment",
                    "action": actions["invoices"],
                },
            },
            "appointments": {
                "total": len(appointments),
                "active": len(active_appointments),
                "completed": len(completed_appointments),
                "overdue": len(overdue_appointments),
                "remaining": len(remaining_appointments),
                "action": actions["schedule"],
            },
            "upcomingSchedule": [
                self._format_schedule_event(event, user_tz, today, now_naive)
                for event in upcoming_schedule_events
            ],
            "performance": {
                "receivables": {
                    "value": money(sum(receivable_moves.mapped("amount_residual_signed"))),
                    "sub": f"{len(receivable_moves)} invoices open",
                    "action": actions["invoices"],
                },
                "upcomingJobs": {
                    "value": env["project.task"].search_count(upcoming_task_domain),
                    "sub": "Tasks still in progress",
                    "action": actions["tasks"],
                },
                "revenue": {
                    "value": money(revenue_this_month),
                    "sub": "Revenue this month",
                    "action": actions["invoices"],
                },
            },
            "alerts": {
                "overdueInvoices": env["account.move"].search_count(overdue_invoice_domain),
                "lateTasks": env["project.task"].search_count(late_task_domain),
                "upcomingAppointments": env["calendar.event"].search_count([("start", ">=", fields.Datetime.to_string(now_naive))]),
            },
        }

    def _format_money(self, currency, amount):
        symbol = currency.symbol or ""
        rounded = currency.round(amount)
        formatted = f"{abs(rounded):,.0f}" if currency.decimal_places == 0 else f"{abs(rounded):,.2f}"
        sign = "-" if rounded < 0 else ""
        if currency.position == "after":
            return f"{sign}{formatted} {symbol}".strip()
        return f"{sign}{symbol} {formatted}".strip()

    def _format_schedule_event(self, event, user_tz, today, now_naive):
        start_local = pytz.utc.localize(event.start).astimezone(user_tz) if event.start else None
        stop_dt = event.stop or event.start
        if stop_dt and stop_dt < now_naive:
            status = "Overdue"
        elif start_local and start_local.date() == today:
            status = "Today"
        else:
            status = "Upcoming"

        return {
            "id": event.id,
            "name": event.name or "",
            "start_datetime": fields.Datetime.to_string(event.start) if event.start else "",
            "display_time": start_local.strftime("%I:%M %p") if start_local else "",
            "customer_name": event.partner_ids[:1].name or "",
            "location": event.location or "",
            "status": status,
        }
