from odoo import api, fields, models


class BookingFlow(models.Model):
    _name = "booking.flow"
    _description = "Booking Flow"
    _order = "name"

    name = fields.Char(required=True)
    slug = fields.Char(required=True)
    active = fields.Boolean(default=True)
    website_id = fields.Many2one("website")
    create_sale_order = fields.Boolean()
    create_appointment = fields.Boolean()
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    step_ids = fields.One2many("booking.flow.step", "flow_id", string="Steps")

    _sql_constraints = [
        ("slug_unique", "unique(slug)", "The booking flow slug must be unique."),
    ]

    @api.model
    def _get_public_flow_domain(self, slug):
        website = self.env["website"].get_current_website()
        return [
            ("slug", "=", slug),
            ("active", "=", True),
            "|",
            ("website_id", "=", False),
            ("website_id", "=", website.id),
        ]
