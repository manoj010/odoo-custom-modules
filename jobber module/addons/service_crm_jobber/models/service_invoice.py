from odoo import api, fields, models, _


class ServiceInvoice(models.Model):
    _name = "service.invoice"
    _description = "Service Invoice"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "invoice_date desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    sequence = fields.Char(readonly=True, copy=False, default=lambda self: _("New"), tracking=True)
    job_id = fields.Many2one("service.job", tracking=True)
    quote_id = fields.Many2one("service.quote", tracking=True)
    partner_id = fields.Many2one("res.partner", string="Client", required=True, tracking=True)
    invoice_date = fields.Date(default=fields.Date.context_today, tracking=True)
    due_date = fields.Date(tracking=True)
    payment_terms = fields.Char()
    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("awaiting_payment", "Awaiting Payment"),
            ("past_due", "Past Due"),
            ("paid", "Paid"),
            ("bad_debt", "Bad Debt"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many("service.invoice.line", "invoice_id", copy=True)
    subtotal = fields.Monetary(compute="_compute_amounts", store=True, currency_field="currency_id")
    discount = fields.Monetary(currency_field="currency_id")
    tax_amount = fields.Monetary(compute="_compute_amounts", store=True, currency_field="currency_id")
    total_amount = fields.Monetary(compute="_compute_amounts", store=True, currency_field="currency_id")
    balance_amount = fields.Monetary(compute="_compute_amounts", store=True, currency_field="currency_id")
    client_message = fields.Text()
    internal_notes = fields.Text()
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)

    @api.depends("sequence")
    def _compute_name(self):
        for invoice in self:
            invoice.name = invoice.sequence if invoice.sequence != _("New") else _("New Invoice")

    @api.depends("line_ids.subtotal", "discount", "status")
    def _compute_amounts(self):
        for invoice in self:
            invoice.subtotal = sum(invoice.line_ids.mapped("subtotal"))
            invoice.tax_amount = 0.0
            invoice.total_amount = max(invoice.subtotal - invoice.discount + invoice.tax_amount, 0.0)
            invoice.balance_amount = 0.0 if invoice.status == "paid" else invoice.total_amount

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("sequence", _("New")) == _("New"):
                vals["sequence"] = self.env["ir.sequence"].next_by_code("service.invoice") or _("New")
        return super().create(vals_list)

    def action_send(self):
        self.write({"status": "awaiting_payment"})
        return True

    def action_mark_paid(self):
        self.write({"status": "paid"})
        return True

    def action_mark_bad_debt(self):
        self.write({"status": "bad_debt"})
        return True


class ServiceInvoiceLine(models.Model):
    _name = "service.invoice.line"
    _description = "Service Invoice Line"

    invoice_id = fields.Many2one("service.invoice", required=True, ondelete="cascade")
    product_name = fields.Char(required=True)
    description = fields.Text()
    quantity = fields.Float(default=1.0)
    unit_price = fields.Monetary(currency_field="currency_id")
    subtotal = fields.Monetary(compute="_compute_subtotal", store=True, currency_field="currency_id")
    currency_id = fields.Many2one(related="invoice_id.currency_id", store=True)

    @api.depends("quantity", "unit_price")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
