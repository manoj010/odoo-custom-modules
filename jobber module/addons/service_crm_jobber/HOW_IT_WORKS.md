# Service CRM Jobber

This Odoo 18 addon adds a Jobber-style service business workflow for handling website requests, clients, quotes, scheduled jobs, invoices, and dashboard metrics.

## What It Adds

- A backend app menu named `Service CRM`.
- A website snippet named `Service Request Form`.
- A public website form route for creating service requests.
- Service workflow records for requests, quotes, jobs, and invoices.
- Quote, job, and invoice line items with automatic subtotals and totals.
- A schedule view for service jobs.
- A dashboard with operational counts and revenue metrics.
- Mail thread and activity support on main workflow records.

## User Flow

1. A visitor submits the website service request form.
2. Odoo finds an existing customer by email or phone, or creates a new client.
3. Odoo creates a `service.request` record with `source = website` and `status = new`.
4. A staff user reviews the request in `Service CRM -> Requests`.
5. The staff user creates a quote from the request.
6. Quote lines are added and the quote is sent or approved.
7. The quote is converted into a job.
8. The job is scheduled, assigned, completed, and marked as requiring invoicing.
9. An invoice is created from the completed job.
10. The invoice is sent and later marked as paid, bad debt, or left awaiting payment.

## Website Service Request Form

The website form is available as an Odoo website snippet:

```text
Website Editor -> Blocks -> Service CRM -> Service Request Form
```

The snippet posts to:

```text
/service-crm/request/submit
```

Required website fields:

- Full Name
- Email
- Message / Special Instructions

Optional website fields:

- Phone
- Company
- Service Type
- Property Address

After submission, the visitor is redirected to:

```text
/service-crm/request/thank-you
```

If required fields are missing, the visitor is redirected to the same thank-you page with an error state.

## Backend Menus

The main backend app is:

```text
Service CRM
```

Menus included:

- `Home`: dashboard view.
- `Clients`: customer contacts from `res.partner`.
- `Requests`: incoming service requests.
- `Quotes`: service quotes and quote lines.
- `Jobs`: service jobs and job lines.
- `Invoices`: service invoices and invoice lines.
- `Schedule`: calendar, kanban, list, and form views for jobs.
- `Insights`: dashboard metrics.
- `Configuration`: placeholder menu for future settings.

## Service Requests

Requests are stored in:

```text
Service CRM -> Requests
```

Model:

```text
service.request
```

Important fields:

- Customer / client link
- Customer name, email, phone, and company
- Service type
- Property address
- Message
- Requested date
- Salesperson
- Source: `website` or `manual`
- Status: `new`, `assessment_complete`, `quoted`, `converted`, or `lost`
- Related quote and job

Available actions:

- `Create Client`: creates a `res.partner` customer from the request details.
- `Create Quote`: creates a linked `service.quote`.
- `Mark Lost`: moves the request to `lost`.

## Quotes

Quotes are stored in:

```text
Service CRM -> Quotes
```

Model:

```text
service.quote
```

Quote statuses:

- `draft`
- `awaiting_response`
- `changes_requested`
- `approved`
- `converted`
- `rejected`

Quote lines are stored in:

```text
service.quote.line
```

Line fields:

- Product name
- Description
- Quantity
- Unit price
- Subtotal

Available actions:

- `Send`: changes the quote to `awaiting_response`.
- `Approve`: changes the quote to `approved`.
- `Convert To Job`: creates a linked `service.job` and copies quote lines into job lines.
- `Reject`: changes the quote to `rejected`.

Quotes can be converted to jobs only after they are sent or approved.

## Jobs

Jobs are stored in:

```text
Service CRM -> Jobs
```

Model:

```text
service.job
```

Job statuses:

- `unscheduled`
- `upcoming`
- `today`
- `late`
- `action_required`
- `requires_invoicing`
- `completed`
- `cancelled`

Job details include:

- Linked quote and request
- Client
- Property address
- Job type: one-off or recurring
- Scheduled date
- Start and end time
- Assigned user
- Visit instructions
- Job lines
- Total amount
- Notes

Available actions:

- `Schedule`: requires a scheduled date and changes the job to `upcoming`.
- `Complete`: changes the job to `requires_invoicing`.
- `Create Invoice`: creates a linked `service.invoice` and copies job lines into invoice lines.
- `Cancel`: changes the job to `cancelled`.

## Schedule

The schedule menu opens `service.job` records with:

```text
calendar, kanban, list, form
```

Use this view to manage scheduled jobs and field team assignments.

## Invoices

Invoices are stored in:

```text
Service CRM -> Invoices
```

Model:

```text
service.invoice
```

Invoice statuses:

- `draft`
- `awaiting_payment`
- `past_due`
- `paid`
- `bad_debt`

Invoice fields include:

- Linked job and quote
- Client
- Invoice date
- Due date
- Payment terms
- Invoice lines
- Subtotal
- Discount
- Tax amount
- Total amount
- Balance amount
- Client message
- Internal notes

Available actions:

- `Send`: changes the invoice to `awaiting_payment`.
- `Mark Paid`: changes the invoice to `paid` and clears the computed balance.
- `Mark Bad Debt`: changes the invoice to `bad_debt`.

## Dashboard Metrics

The dashboard model is:

```text
service.dashboard
```

It computes:

- New requests count
- Approved quotes count
- Jobs requiring invoicing count
- Invoices awaiting payment count
- Past due invoices amount
- Upcoming jobs amount
- Revenue this month

## Sequences

Records receive automatic sequence numbers from:

```text
data/sequence_data.xml
```

Sequence codes:

- `service.request`
- `service.quote`
- `service.job`
- `service.invoice`

## Frontend Files

Website form assets live in:

```text
static/src/
```

Important files:

- `static/src/js/request_snippet.js`: frontend behavior for the service request snippet.
- `static/src/scss/request_snippet.scss`: website request form styling.
- `static/src/img/service_request_thumbnail.svg`: website editor snippet thumbnail.

Backend styles live in:

```text
static/src/scss/backend.scss
```

## Controller Routes

### `/service-crm/request/submit`

Type: HTTP  
Auth: public  
Website: true  
Methods: GET and POST  
CSRF: disabled

GET requests redirect to `/`.

POST requests validate required fields, find or create a client, create a website service request, and redirect to the thank-you page.

### `/service-crm/request/thank-you`

Type: HTTP  
Auth: public  
Website: true

Renders the thank-you template. If the `error` query parameter is present, the template displays the missing-fields state.

## Updating After Code Changes

For this Docker setup, update the module with:

```powershell
docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d odoo-jobber_module-db -u service_crm_jobber --db_host=db --db_user=odoo --db_password=odoo --stop-after-init
```

Then refresh the website page. If browser assets look stale, use a hard refresh.

## Future Integration Points

This module currently stores its own workflow records. Later it can integrate more deeply with:

- CRM: create or link Odoo CRM leads and opportunities.
- Sales: convert quotes into native sale orders.
- Accounting: convert service invoices into native Odoo invoices.
- Calendar: create calendar events for scheduled jobs.
- Timesheets: record technician time against jobs.
- Payments: collect online payments from invoices.
- Mail/SMS: send quote, job, and invoice notifications.
