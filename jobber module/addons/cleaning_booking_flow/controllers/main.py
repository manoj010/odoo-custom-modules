from datetime import datetime, time, timedelta

from odoo import fields
from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
import pytz

FALLBACK_TIMES = ["09:00 AM", "12:00 PM", "02:00 PM", "04:00 PM", "06:00 PM", "08:00 PM"]

class CleaningBookingController(http.Controller):
    @http.route("/cleaning-booking/services", type="json", auth="public", website=True)
    def services(self):
        services = request.env["appointment.type"].sudo().search(
            [("active", "=", True), ("is_cleaning_service", "=", True)],
            order="sequence, id"
        )
        return [
            {
                "id": service.id,
                "name": service.name,
                "description": service.description or "",  # or your custom field
                "icon_class": service.icon_class or "fa fa-sparkles",
                "price": service.price,
                "duration_minutes": int(service.appointment_duration * 60),
            }
            for service in services
        ]


#     @http.route("/cleaning-booking/services", type="json", auth="public", website=True)
#     def services(self):
#         services = request.env["cleaning.booking.service"].sudo().search(
#             [("active", "=", True)], order="sequence, id"
#         )
#         return [
#             {
#                 "id": service.id,
#                 "name": service.name,
#                 "description": service.description or "",
#                 "icon_class": service.icon_class or "fa fa-sparkles",
#                 "price": service.price,
#                 "duration_minutes": service.duration_minutes,
#             }
#             for service in services
#         ]

    # @http.route("/cleaning-booking/availability", type="json", auth="public", website=True)
    # def availability(self, **payload):
    #     service_id = int(payload.get("service_id") or 0)
    #     booking_date = self._parse_booking_date(payload.get("date"))
    #     if not service_id or not booking_date:
    #         return {"success": False, "message": "Please choose a service and date.", "slots": []}

    #     today = fields.Date.context_today(request.env.user)
    #     if booking_date < today:
    #         return {"success": False, "message": "Please choose today or a future date.", "slots": []}

    #     service = request.env["appointment.type"].sudo().browse(service_id)
    #     if not service.exists() or not service.active:
    #         return {"success": False, "message": "Please choose an available service.", "slots": []}

    #     slots = self._get_available_slots(service, booking_date)
    #     return {"success": True, "slots": slots}

    # @http.route(
    #     "/cleaning-booking/create",
    #     type="json",
    #     auth="public",
    #     website=True,
    #     csrf=False,
    # )
    # def create_booking(self, **payload):
    #     service_id = int(payload.get("service_id") or 0)
    #     customer_name = (payload.get("customer_name") or "").strip()
    #     email = (payload.get("email") or "").strip()
    #     phone = (payload.get("phone") or "").strip()

    #     if not service_id or not customer_name or not email or not phone:
    #         return {
    #             "success": False,
    #             "message": "Please complete service, name, email, and phone.",
    #         }

    #     service = request.env["cleaning.booking.service"].sudo().browse(service_id)
    #     if not service.exists() or not service.active:
    #         return {"success": False, "message": "Please choose an available service."}

    #     booking_date = self._parse_booking_date(payload.get("booking_date"))
    #     booking_time = (payload.get("booking_time") or "").strip()
    #     today = fields.Date.context_today(request.env.user)
    #     if not booking_date or booking_date < today:
    #         return {"success": False, "message": "Please choose today or a future date."}

    #     available_slots = self._get_available_slots(service, booking_date)
    #     if booking_time not in available_slots:
    #         return {"success": False, "message": "Please choose an available time."}

    #     booking = request.env["cleaning.booking"].sudo().create(
    #         {
    #             "service_id": service.id,
    #             "customer_name": customer_name,
    #             "email": email,
    #             "phone": phone,
    #             "location": (payload.get("location") or "").strip(),
    #             "message": (payload.get("message") or "").strip(),
    #             "booking_date": booking_date,
    #             "booking_time": booking_time,
    #             "price": float(payload.get("price") or service.price or 0.0),
    #             "payment_status": "pending",
    #             "state": "confirmed",
    #         }
    #     )
    #     return {
    #         "success": True,
    #         "booking_id": booking.id,
    #         "message": "Your cleaning service has been successfully booked.",
    #     }

    @http.route("/cleaning-booking/availability", type="json", auth="public", website=True)
    def availability(self, **payload):
        service_id = int(payload.get("service_id") or 0)
        booking_date = self._parse_booking_date(payload.get("date"))
        if not service_id or not booking_date:
            return {"success": False, "message": "Please choose a service and date.", "slots": []}

        today = fields.Date.context_today(request.env.user)
        if booking_date < today:
            return {"success": False, "message": "Please choose today or a future date.", "slots": []}

        service = request.env["appointment.type"].sudo().browse(service_id)
        if not service.exists() or not service.active or not service.is_cleaning_service:
            return {"success": False, "message": "Please choose an available service.", "slots": []}

        slots = self._get_available_slots(service, booking_date)
        return {"success": True, "slots": slots}

    # @http.route(
    #     "/cleaning-booking/create",
    #     type="json",
    #     auth="public",
    #     website=True,
    #     csrf=False,
    # )
    # def create_booking(self, **payload):
    #     service_id = int(payload.get("service_id") or 0)
    #     customer_name = (payload.get("customer_name") or "").strip()
    #     email = (payload.get("email") or "").strip()
    #     phone = (payload.get("phone") or "").strip()

    #     if not service_id or not customer_name or not email or not phone:
    #         return {
    #             "success": False,
    #             "message": "Please complete service, name, email, and phone.",
    #         }

    #     service = request.env["appointment.type"].sudo().browse(service_id)
    #     if not service.exists() or not service.active or not service.is_cleaning_service:
    #         return {"success": False, "message": "Please choose an available service."}

    #     booking_date = self._parse_booking_date(payload.get("booking_date"))
    #     booking_time = (payload.get("booking_time") or "").strip()
    #     today = fields.Date.context_today(request.env.user)
    #     if not booking_date or booking_date < today:
    #         return {"success": False, "message": "Please choose today or a future date."}

    #     available_slots = self._get_available_slots(service, booking_date)
    #     if booking_time not in available_slots:
    #         return {"success": False, "message": "Please choose an available time."}

    #     booking = request.env["cleaning.booking"].sudo().create(
    #         {
    #             "service_id": service.id,
    #             "customer_name": customer_name,
    #             "email": email,
    #             "phone": phone,
    #             "location": (payload.get("location") or "").strip(),
    #             "message": (payload.get("message") or "").strip(),
    #             "booking_date": booking_date,
    #             "booking_time": booking_time,
    #             "price": float(payload.get("price") or service.price or 0.0),
    #             "payment_status": "pending",
    #             "state": "confirmed",
    #         }
    #     )
    #     return {
    #         "success": True,
    #         "booking_id": booking.id,
    #         "message": "Your cleaning service has been successfully booked.",
    #     }

    
    @http.route("/cleaning-booking/create", type="json", auth="public", website=True, csrf=False,)
    def create_booking(self, **payload):
        service_id = int(payload.get("service_id") or 0)
        customer_name = (payload.get("customer_name") or "").strip()
        email = (payload.get("email") or "").strip()
        phone = (payload.get("phone") or "").strip()

        if not service_id or not customer_name or not email or not phone:
            return {"success": False, "message": "Please complete service, name, email, and phone."}

        service = request.env["appointment.type"].sudo().browse(service_id)
        if not service.exists() or not service.active or not service.is_cleaning_service:
            return {"success": False, "message": "Please choose an available service."}

        booking_date = self._parse_booking_date(payload.get("booking_date"))
        booking_time = (payload.get("booking_time") or "").strip()
        today = fields.Date.context_today(request.env.user)
        if not booking_date or booking_date < today:
            return {"success": False, "message": "Please choose today or a future date."}

        available_slots = self._get_available_slots(service, booking_date)
        if booking_time not in available_slots:
            return {"success": False, "message": "Please choose an available time."}

        # Convert to UTC for calendar.event
        try:
            hour, minute = map(int, booking_time.split(":"))
        except ValueError:
            hour, minute = 9, 0

        tz_name = service.appointment_tz or "UTC"
        local_tz = pytz.timezone(tz_name)
        local_start = local_tz.localize(
            datetime(booking_date.year, booking_date.month, booking_date.day, hour, minute)
        )
        local_stop = local_start + timedelta(hours=service.appointment_duration or 1.0)
        start_utc = local_start.astimezone(pytz.utc).replace(tzinfo=None)
        stop_utc = local_stop.astimezone(pytz.utc).replace(tzinfo=None)

        # Find or create partner
        Partner = request.env["res.partner"].sudo()
        partner = Partner.search([("email", "=", email)], limit=1)
        if not partner:
            partner = Partner.create({
                "name": customer_name,
                "email": email,
                "phone": phone,
            })

        event = request.env["calendar.event"].sudo().create({
            "name": f"{service.name} – {customer_name}",
            "start": start_utc,
            "stop": stop_utc,
            "location": (payload.get("location") or "").strip(),
            "description": (payload.get("message") or "").strip(),
            "partner_ids": [(4, partner.id)],
            "appointment_type_id": service.id,
            "price": float(payload.get("price") or service.price or 0.0),
            "payment_status": "pending",
            "is_cleaning_booking": True,
        })

        return {
            "success": True,
            "booking_id": event.id,
            "message": "Your cleaning service has been successfully booked.",
        }

    def _parse_booking_date(self, value):
        try:
            return fields.Date.to_date(value)
        except Exception:
            return False

    # def _get_available_slots(self, service, booking_date):
    #     Availability = request.env["cleaning.booking.availability"].sudo()
    #     rules = Availability.search(
    #         [
    #             ("service_id", "=", service.id),
    #             ("weekday", "=", str(booking_date.weekday())),
    #             ("active", "=", True),
    #         ],
    #         order="start_time, id",
    #     )
    #     slots = []
    #     if rules:
    #         for rule in rules:
    #             slots.extend(self._build_rule_slots(rule))
    #     else:
    #         slots = list(FALLBACK_TIMES)

    #     slots = list(dict.fromkeys(slots))
    #     booked_times = set(
    #         request.env["cleaning.booking"]
    #         .sudo()
    #         .search(
    #             [
    #                 ("service_id", "=", service.id),
    #                 ("booking_date", "=", booking_date),
    #                 ("booking_time", "in", slots),
    #                 ("state", "!=", "cancelled"),
    #             ]
    #         )
    #         .mapped("booking_time")
    #     )
    #     return [slot for slot in slots if slot not in booked_times]

    def _get_available_slots(self, service, booking_date):
        Availability = request.env["cleaning.booking.availability"].sudo()
        rules = Availability.search(
            [
                ("service_id", "=", service.id),
                ("weekday", "=", str(booking_date.weekday())),
                ("active", "=", True),
            ],
            order="start_time, id",
        )

        # duration in minutes from service (hours * 60)
        duration_minutes = int(service.appointment_duration * 60) if service.appointment_duration else 60

        slots = []
        if rules:
            for rule in rules:
                slots.extend(self._build_rule_slots(rule, duration_minutes))
        else:
            slots = list(FALLBACK_TIMES)

        slots = list(dict.fromkeys(slots))

        booked_starts = set(
            request.env["calendar.event"]
            .sudo()
            .with_context(active_test=False)
            .search([
                ("appointment_type_id", "=", service.id),
                ("start", ">=", datetime.combine(booking_date, time.min)),
                ("start", "<", datetime.combine(booking_date + timedelta(days=1), time.min)),
                ("is_cleaning_booking", "=", True),
            ])
            .mapped("start")
        )

        tz_name = service.appointment_tz or "UTC"
        local_tz = pytz.timezone(tz_name)
        booked_times = set()
        for start_utc in booked_starts:
            if isinstance(start_utc, str):
                start_utc = fields.Datetime.from_string(start_utc)
            local_dt = pytz.utc.localize(start_utc).astimezone(local_tz)
            booked_times.add(local_dt.strftime("%I:%M %p"))

        return [slot for slot in slots if slot not in booked_times]

    def _build_rule_slots(self, rule, interval_minutes=60):
        # interval_minutes comes directly from service duration (already converted)
        if rule.end_time <= rule.start_time or interval_minutes <= 0:
            return []

        current = self._float_hour_to_datetime(rule.start_time)
        end = self._float_hour_to_datetime(rule.end_time)
        interval = timedelta(minutes=interval_minutes)
        slots = []
        while current < end:
            slots.append(current.strftime("%I:%M %p"))
            current += interval
        return slots
    
    def _float_hour_to_datetime(self, value):
        hours = int(value)
        minutes = int(round((value - hours) * 60))
        return datetime.combine(datetime.today().date(), time(hour=hours, minute=minutes))
