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


class CleaningBooking(models.Model):
    _name = "cleaning.booking"
    _description = "Cleaning Booking"
    _order = "create_date desc"

    service_id = fields.Many2one("cleaning.booking.service", required=True)
    customer_name = fields.Char(required=True)
    email = fields.Char(required=True)
    phone = fields.Char()
    location = fields.Char()
    message = fields.Text()
    booking_date = fields.Date()
    booking_time = fields.Char()
    price = fields.Float()
    payment_status = fields.Selection(
        [
            ("pending", "Pending"),
            ("paid", "Paid"),
            ("failed", "Failed"),
        ],
        default="pending",
        required=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
    )
    notes = fields.Text()
