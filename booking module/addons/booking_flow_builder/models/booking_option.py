from odoo import fields, models


class BookingFlowOption(models.Model):
    _name = "booking.flow.option"
    _description = "Booking Flow Option"
    _order = "sequence, id"

    step_id = fields.Many2one(
        "booking.flow.step",
        required=True,
        ondelete="cascade",
    )
    label = fields.Char(required=True)
    image = fields.Binary()
    sequence = fields.Integer(default=10)
    pricing_type = fields.Selection(
        [
            ("none", "None"),
            ("fixed", "Fixed"),
            ("percentage", "Percentage"),
        ],
        required=True,
        default="none",
    )
    pricing_value = fields.Float()
    active = fields.Boolean(default=True)
