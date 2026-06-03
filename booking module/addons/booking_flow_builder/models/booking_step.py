from odoo import fields, models


class BookingFlowStep(models.Model):
    _name = "booking.flow.step"
    _description = "Booking Flow Step"
    _order = "sequence, id"

    flow_id = fields.Many2one(
        "booking.flow",
        required=True,
        ondelete="cascade",
    )
    title = fields.Char(required=True)
    subtitle = fields.Text()
    step_type = fields.Selection(
        [
            ("single_choice", "Single Choice"),
            ("multi_choice", "Multi Choice"),
            ("text", "Text"),
            ("textarea", "Textarea"),
            ("number", "Number"),
            ("info", "Info"),
            ("review", "Review"),
        ],
        required=True,
        default="single_choice",
    )
    sequence = fields.Integer(default=10)
    required = fields.Boolean(default=True)
    active = fields.Boolean(default=True)
    option_ids = fields.One2many("booking.flow.option", "step_id", string="Options")
