from odoo import api, fields, models


class BookingSession(models.Model):
    _name = "booking.session"
    _description = "Booking Session"
    _order = "create_date desc, id desc"

    flow_id = fields.Many2one("booking.flow", required=True)
    partner_id = fields.Many2one("res.partner")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
    )
    current_step_id = fields.Many2one("booking.flow.step")
    total_price = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    sale_order_id = fields.Many2one("sale.order")
    answer_ids = fields.One2many("booking.session.answer", "session_id", string="Answers")
    customer_name = fields.Char()
    customer_email = fields.Char()
    customer_phone = fields.Char()
    customer_note = fields.Text()
    booking_datetime = fields.Datetime()

    @api.model
    def _partner_from_customer(self, values):
        partner = self.env.user.partner_id if not self.env.user._is_public() else False
        email = (values.get("customer_email") or "").strip()
        phone = (values.get("customer_phone") or "").strip()
        name = (values.get("customer_name") or "").strip()
        note = (values.get("customer_note") or "").strip()

        if not partner and (email or phone):
            domain = []
            if email:
                domain.append(("email", "=", email))
            if phone:
                if domain:
                    domain = ["|"] + domain
                domain.append(("phone", "=", phone))
            partner = self.env["res.partner"].sudo().search(domain, limit=1)

        if not partner and (name or email or phone):
            partner = self.env["res.partner"].sudo().create(
                {
                    "name": name or email or phone,
                    "email": email,
                    "phone": phone,
                    "comment": note,
                }
            )
        return partner

    @api.model
    def _create_sale_order_for_session(self, session):
        if not session.flow_id.create_sale_order or not session.partner_id:
            return False
        product = self.env.ref("sale.advance_product_0", raise_if_not_found=False)
        order = self.env["sale.order"].sudo().create(
            {
                "partner_id": session.partner_id.id,
                "currency_id": session.currency_id.id,
                "origin": "Booking Session %s" % session.id,
            }
        )
        if product and session.total_price:
            self.env["sale.order.line"].sudo().create(
                {
                    "order_id": order.id,
                    "product_id": product.id,
                    "name": session.flow_id.name,
                    "product_uom_qty": 1,
                    "price_unit": session.total_price,
                }
            )
        session.sudo().sale_order_id = order.id
        return order


class BookingSessionAnswer(models.Model):
    _name = "booking.session.answer"
    _description = "Booking Session Answer"
    _order = "id"

    session_id = fields.Many2one(
        "booking.session",
        required=True,
        ondelete="cascade",
    )
    step_id = fields.Many2one("booking.flow.step", required=True)
    option_id = fields.Many2one("booking.flow.option")
    text_value = fields.Text()
    numeric_value = fields.Float()
