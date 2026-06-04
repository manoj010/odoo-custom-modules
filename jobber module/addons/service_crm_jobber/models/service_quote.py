from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ServiceQuote(models.Model):
    _name = "service.quote"
    _description = "Service Quote"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "quote_date desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    sequence = fields.Char(readonly=True, copy=False, default=lambda self: _("New"), tracking=True)
    request_id = fields.Many2one("service.request", tracking=True)
    partner_id = fields.Many2one("res.partner", string="Client", required=True, tracking=True)
    property_address = fields.Text()
    salesperson_id = fields.Many2one("res.users", default=lambda self: self.env.user, tracking=True)
    quote_date = fields.Date(default=fields.Date.context_today, tracking=True)
    valid_until = fields.Date()
    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("awaiting_response", "Awaiting Response"),
            ("changes_requested", "Changes Requested"),
            ("approved", "Approved"),
            ("converted", "Converted"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many("service.quote.line", "quote_id", copy=True)
    subtotal = fields.Monetary(compute="_compute_amounts", store=True, currency_field="currency_id")
    tax_amount = fields.Monetary(compute="_compute_amounts", store=True, currency_field="currency_id")
    total_amount = fields.Monetary(compute="_compute_amounts", store=True, currency_field="currency_id")
    notes = fields.Text()
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)

    @api.depends("sequence", "partner_id")
    def _compute_name(self):
        for quote in self:
            quote.name = quote.sequence if quote.sequence != _("New") else _("New Quote")

    @api.depends("line_ids.subtotal")
    def _compute_amounts(self):
        for quote in self:
            quote.subtotal = sum(quote.line_ids.mapped("subtotal"))
            quote.tax_amount = quote.subtotal * 0.0
            quote.total_amount = quote.subtotal + quote.tax_amount

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("sequence", _("New")) == _("New"):
                vals["sequence"] = self.env["ir.sequence"].next_by_code("service.quote") or _("New")
        return super().create(vals_list)

    def action_send(self):
        self.write({"status": "awaiting_response"})
        return True

    def action_approve(self):
        self.write({"status": "approved"})
        return True

    def action_convert_to_job(self):
        self.ensure_one()
        if self.status not in ("approved", "awaiting_response"):
            raise UserError(_("Approve or send the quote before converting it to a job."))
        job = self.env["service.job"].create(
            {
                "quote_id": self.id,
                "request_id": self.request_id.id,
                "partner_id": self.partner_id.id,
                "property_address": self.property_address,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_name": line.product_name,
                            "description": line.description,
                            "quantity": line.quantity,
                            "unit_price": line.unit_price,
                        },
                    )
                    for line in self.line_ids
                ],
                "notes": self.notes,
            }
        )
        self.write({"status": "converted"})
        if self.request_id:
            self.request_id.write({"job_id": job.id, "status": "converted"})
        return {
            "type": "ir.actions.act_window",
            "name": _("Job"),
            "res_model": "service.job",
            "view_mode": "form",
            "res_id": job.id,
        }

    def action_reject(self):
        self.write({"status": "rejected"})
        return True


class ServiceQuoteLine(models.Model):
    _name = "service.quote.line"
    _description = "Service Quote Line"

    quote_id = fields.Many2one("service.quote", required=True, ondelete="cascade")
    product_name = fields.Char(required=True)
    description = fields.Text()
    quantity = fields.Float(default=1.0)
    unit_price = fields.Monetary(currency_field="currency_id")
    subtotal = fields.Monetary(compute="_compute_subtotal", store=True, currency_field="currency_id")
    currency_id = fields.Many2one(related="quote_id.currency_id", store=True)

    @api.depends("quantity", "unit_price")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
