from odoo import api, fields, models


class ServiceDashboard(models.Model):
    _name = "service.dashboard"
    _description = "Service CRM Dashboard"

    name = fields.Char(default="Service CRM Dashboard")
    new_requests_count = fields.Integer(compute="_compute_metrics")
    approved_quotes_count = fields.Integer(compute="_compute_metrics")
    jobs_requiring_invoicing_count = fields.Integer(compute="_compute_metrics")
    invoices_awaiting_payment_count = fields.Integer(compute="_compute_metrics")
    past_due_invoices_amount = fields.Monetary(compute="_compute_metrics", currency_field="currency_id")
    upcoming_jobs_amount = fields.Monetary(compute="_compute_metrics", currency_field="currency_id")
    revenue_this_month = fields.Monetary(compute="_compute_metrics", currency_field="currency_id")
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)

    @api.depends_context("uid")
    def _compute_metrics(self):
        Request = self.env["service.request"]
        Quote = self.env["service.quote"]
        Job = self.env["service.job"]
        Invoice = self.env["service.invoice"]
        today = fields.Date.context_today(self)
        month_start = today.replace(day=1)
        for dashboard in self:
            dashboard.new_requests_count = Request.search_count([("status", "=", "new")])
            dashboard.approved_quotes_count = Quote.search_count([("status", "=", "approved")])
            dashboard.jobs_requiring_invoicing_count = Job.search_count([("status", "=", "requires_invoicing")])
            dashboard.invoices_awaiting_payment_count = Invoice.search_count([("status", "=", "awaiting_payment")])
            dashboard.past_due_invoices_amount = sum(
                Invoice.search([("status", "=", "past_due")]).mapped("balance_amount")
            )
            dashboard.upcoming_jobs_amount = sum(
                Job.search([("status", "in", ["upcoming", "today"])]).mapped("total_amount")
            )
            dashboard.revenue_this_month = sum(
                Invoice.search(
                    [
                        ("status", "=", "paid"),
                        ("invoice_date", ">=", month_start),
                        ("invoice_date", "<=", today),
                    ]
                ).mapped("total_amount")
            )
