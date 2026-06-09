from odoo import http
from odoo.http import request


class CleaningBookingController(http.Controller):
    @http.route("/cleaning-booking/services", type="json", auth="public", website=True)
    def services(self):
        services = request.env["cleaning.booking.service"].sudo().search(
            [("active", "=", True)], order="sequence, id"
        )
        return [
            {
                "id": service.id,
                "name": service.name,
                "description": service.description or "",
                "icon_class": service.icon_class or "fa fa-sparkles",
                "price": service.price,
                "duration_minutes": service.duration_minutes,
            }
            for service in services
        ]

    @http.route(
        "/cleaning-booking/create",
        type="json",
        auth="public",
        website=True,
        csrf=False,
    )
    def create_booking(self, **payload):
        service_id = int(payload.get("service_id") or 0)
        customer_name = (payload.get("customer_name") or "").strip()
        email = (payload.get("email") or "").strip()
        phone = (payload.get("phone") or "").strip()

        if not service_id or not customer_name or not email or not phone:
            return {
                "success": False,
                "message": "Please complete service, name, email, and phone.",
            }

        service = request.env["cleaning.booking.service"].sudo().browse(service_id)
        if not service.exists() or not service.active:
            return {"success": False, "message": "Please choose an available service."}

        booking = request.env["cleaning.booking"].sudo().create(
            {
                "service_id": service.id,
                "customer_name": customer_name,
                "email": email,
                "phone": phone,
                "location": (payload.get("location") or "").strip(),
                "message": (payload.get("message") or "").strip(),
                "booking_date": payload.get("booking_date") or False,
                "booking_time": (payload.get("booking_time") or "").strip(),
                "price": float(payload.get("price") or service.price or 0.0),
                "payment_status": "pending",
                "state": "confirmed",
            }
        )
        return {
            "success": True,
            "booking_id": booking.id,
            "message": "Your cleaning service has been successfully booked.",
        }
