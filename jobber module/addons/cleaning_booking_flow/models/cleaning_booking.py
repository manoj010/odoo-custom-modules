from odoo import fields, models


class CleaningBookingService(models.Model):
    _name = "cleaning.booking.service"
    _description = "Cleaning Booking Service"
    _order = "sequence, id"

    name = fields.Char(required=True)
    description = fields.Text()
    icon_class = fields.Char(default="fa fa-sparkles")
    price = fields.Float()
    duration_minutes = fields.Integer(default=60)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)


class AppointmentType(models.Model):
    _inherit = "appointment.type"

    description = fields.Text()
    icon_class = fields.Char(default="fa fa-sparkles")
    # 'name', 'sequence', 'active' already exist on appointment.type
    # 'price' — add if not already on your module
    price = fields.Float()
    is_cleaning_service = fields.Boolean(default=True)


class CleaningBookingAvailability(models.Model):
    _name = "cleaning.booking.availability"
    _description = "Cleaning Booking Availability"
    _order = "service_id, weekday, start_time"

    # service_id = fields.Many2one("cleaning.booking.service", required=True, ondelete="cascade")
    # In CleaningBookingAvailability
    service_id = fields.Many2one("appointment.type", required=True, ondelete="cascade")
    weekday = fields.Selection(
        [
            ("0", "Monday"),
            ("1", "Tuesday"),
            ("2", "Wednesday"),
            ("3", "Thursday"),
            ("4", "Friday"),
            ("5", "Saturday"),
            ("6", "Sunday"),
        ],
        required=True,
        default="0",
    )
    start_time = fields.Float(required=True, default=9.0)
    end_time = fields.Float(required=True, default=18.0)
    slot_interval_minutes = fields.Float(
        related="service_id.appointment_duration",
        string="Slot Interval (hrs)",
        store=True,
        readonly=False,
    )
    active = fields.Boolean(default=True)


# class CleaningBooking(models.Model):
#     _name = "cleaning.booking"
#     _description = "Cleaning Booking"
#     _order = "create_date desc"

#     # service_id = fields.Many2one("cleaning.booking.service", required=True)
#     service_id = fields.Many2one("appointment.type", required=True)
#     customer_name = fields.Char(required=True)
#     email = fields.Char(required=True)
#     phone = fields.Char()
#     location = fields.Char()
#     message = fields.Text()
#     booking_date = fields.Date()
#     booking_time = fields.Char()
#     price = fields.Float()
#     payment_status = fields.Selection(
#         [
#             ("pending", "Pending"),
#             ("paid", "Paid"),
#             ("failed", "Failed"),
#         ],
#         default="pending",
#         required=True,
#     )
#     state = fields.Selection(
#         [
#             ("draft", "Draft"),
#             ("confirmed", "Confirmed"),
#             ("cancelled", "Cancelled"),
#         ],
#         default="draft",
#         required=True,
#     )
#     notes = fields.Text()


class CleaningBooking(models.Model):
    _inherit = "calendar.event"

    price = fields.Float(string="Price")
    payment_status = fields.Selection(
        [("pending", "Pending"), ("paid", "Paid"), ("failed", "Failed")],
        default="pending",
    )
    is_cleaning_booking = fields.Boolean(default=False)
