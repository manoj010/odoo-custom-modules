# Booking Flow Builder

`booking_flow_builder` is a custom Odoo 18 Website module for creating reusable booking wizards without writing code for each booking flow.

Administrators create flows, steps, and options in the backend. Website visitors complete the flow step by step on the public website. When the visitor submits, the module stores the booking session, customer details, answers, selected options, total price, partner link, and optional sale order.

## Features

- Backend management for booking flows, steps, options, sessions, and answers.
- Public website wizard at `/booking/<slug>`.
- Demo flow at `/booking/demo`.
- Ordered multi-step flow.
- Supported step types:
  - Single choice
  - Multi choice
  - Text
  - Textarea
  - Number
  - Info
  - Review
- Required field validation.
- Live total price calculation.
- Customer details collection before submit.
- Partner find/create logic.
- Completed booking persistence in PostgreSQL.
- Optional sale order creation.
- Website editor snippet named `Booking Flow`.

## Dependencies

The module depends on:

```text
website
web
sale_management
calendar
```

It does not depend on the Odoo appointment module.

## Installation

1. Copy or mount this repository so Odoo can see the `addons` directory.
2. Make sure the Odoo addons path includes the custom addons folder.

Example Docker mount:

```yaml
volumes:
  - ./addons:/mnt/extra-addons
```

Example Odoo config:

```ini
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
```

3. Restart Odoo if needed.
4. Open Odoo Apps.
5. Click `Update Apps List`.
6. Search for `Booking Flow Builder`.
7. Install the module.

For the local project used during development, Odoo runs at:

```text
http://localhost:8073
```

## Backend Menus

After installation, open:

```text
Booking Flows
```

Available menus:

```text
Booking Flows > Configuration > Flows
Booking Flows > Sessions > All Sessions
```

## Creating A Booking Flow

Open:

```text
Booking Flows > Configuration > Flows
```

Create a new flow and fill:

- `Name`: the backend display name.
- `Slug`: the public URL slug.
- `Active`: must be enabled for public use.
- `Website`: optional website restriction.
- `Currency`: currency used for pricing.
- `Create Sale Order`: enable if a sale order should be created after submit.
- `Create Appointment`: reserved for future behavior in this v1 module.

Example:

```text
Name: Hotel Room Booking
Slug: hotel-room
```

The public URL becomes:

```text
http://localhost:8073/booking/hotel-room
```

## Creating Steps

Inside a flow, use the `Steps` tab.

Each step has:

- `Title`
- `Subtitle`
- `Step Type`
- `Sequence`
- `Required`
- `Active`
- `Options`

Use the sequence handle to reorder steps.

Recommended flow structure:

```text
1. Service or product selection
2. Additional details
3. Notes or requirements
4. Review
```

Keep a `Review` step at the end so visitors can confirm their booking and enter customer details.

## Step Types

### Single Choice

Visitor selects one option.

Use this for service, package, room type, vehicle type, or plan selection.

### Multi Choice

Visitor selects multiple options.

Use this for add-ons or extra services.

### Text

Visitor enters a short text value.

Use this for names, codes, short labels, or simple custom fields.

### Textarea

Visitor enters longer text.

Use this for notes, requirements, addresses, or messages.

### Number

Visitor enters a numeric value.

Use this for quantity, guest count, duration, or similar numeric inputs.

### Info

Displays informational text and lets the visitor continue.

### Review

Shows selected answers and collects customer details before final submit.

## Creating Options

Options belong to a step.

Each option has:

- `Label`
- `Image`
- `Sequence`
- `Pricing Type`
- `Pricing Value`
- `Active`

Pricing types:

```text
none
fixed
percentage
```

For most use cases, use `fixed`.

Example:

```text
Option: Standard Booking
Pricing Type: Fixed
Pricing Value: 100
```

## Public Website Flow

A visitor opens:

```text
/booking/<slug>
```

Example:

```text
http://localhost:8073/booking/demo
```

Flow behavior:

1. The page renders `booking_flow_builder.booking_flow_page`.
2. The page includes:

   ```html
   <div class="o_booking_flow_app" data-flow-slug="demo"></div>
   ```

3. The OWL frontend app loads the flow using:

   ```text
   /booking/api/flow/<slug>
   ```

4. Visitor completes each step.
5. Live price updates from selected options.
6. Visitor reaches review screen.
7. Visitor enters:
   - Customer name
   - Email
   - Phone
   - Notes or message
8. Visitor submits.
9. Frontend sends data to:

   ```text
   /booking/api/submit
   ```

10. Odoo creates the booking session and answers.

## Customer Data Saved

On submit, the module saves:

- Selected flow
- Customer name
- Customer email
- Customer phone
- Customer note
- Partner
- All selected answers
- Selected options
- Text answers
- Numeric answers
- Total calculated price
- State as `completed`
- Sale order if enabled on the flow

Saved bookings are visible from:

```text
Booking Flows > Sessions > All Sessions
```

## Partner Logic

When a booking is submitted:

1. If the visitor is logged in, their partner is used.
2. If the visitor is public and provides email or phone, Odoo searches for an existing partner.
3. If no partner is found, a new `res.partner` is created.
4. The partner is linked to the booking session.

## Optional Sale Order Creation

If `Create Sale Order` is enabled on the flow:

1. A sale order is created for the linked partner.
2. The sale order is linked to the booking session.
3. If Odoo's sale advance product is available and the total is greater than zero, one order line is added using the booking flow name and total price.

The linked sale order appears on the booking session form.

## Website Snippet

The module adds a Website editor block named:

```text
Booking Flow
```

To use it:

1. Open a website page.
2. Click `Edit`.
3. Open the `Blocks` panel.
4. Search for `Booking Flow`.
5. Drag the block onto the page.
6. Save.

The snippet currently uses:

```html
data-flow-slug="demo"
```

To point it at another flow, edit the snippet markup or add a future snippet option for selecting a flow slug.

## Demo Flow

The demo data creates one active flow:

```text
Name: Demo Booking
Slug: demo
```

Demo steps:

```text
1. Choose a service
2. Add a request
3. Almost done
```

Demo options:

```text
Consultation       50
Standard Booking   100
Premium Booking    180
```

Test URL:

```text
http://localhost:8073/booking/demo
```

## API Endpoints

### Render Booking Page

```text
GET /booking/<string:slug>
```

Renders the public booking page.

### Load Flow Data

```text
POST /booking/api/flow/<string:slug>
```

Returns JSON flow data:

- Flow id, name, slug, currency
- Active steps
- Active options
- Option pricing data

### Submit Booking

```text
POST /booking/api/submit
```

Expected payload:

```json
{
  "flow_id": 1,
  "answers": [
    {
      "step_id": 1,
      "option_id": 1
    },
    {
      "step_id": 2,
      "text_value": "Need a morning slot"
    }
  ],
  "total_price": 50,
  "customer_name": "Customer Name",
  "customer_email": "customer@example.com",
  "customer_phone": "1234567890",
  "customer_note": "Optional note"
}
```

Success response:

```json
{
  "success": true,
  "session_id": 1
}
```

## Data Models

### booking.flow

Main booking flow.

Important fields:

- `name`
- `slug`
- `active`
- `website_id`
- `create_sale_order`
- `create_appointment`
- `currency_id`
- `step_ids`

### booking.flow.step

Ordered step inside a flow.

Important fields:

- `flow_id`
- `title`
- `subtitle`
- `step_type`
- `sequence`
- `required`
- `active`
- `option_ids`

### booking.flow.option

Selectable option inside a step.

Important fields:

- `step_id`
- `label`
- `image`
- `sequence`
- `pricing_type`
- `pricing_value`
- `active`

### booking.session

Saved visitor booking.

Important fields:

- `flow_id`
- `partner_id`
- `customer_name`
- `customer_email`
- `customer_phone`
- `customer_note`
- `state`
- `current_step_id`
- `total_price`
- `currency_id`
- `sale_order_id`
- `answer_ids`

### booking.session.answer

Saved answer for a booking session.

Important fields:

- `session_id`
- `step_id`
- `option_id`
- `text_value`
- `numeric_value`

## Security

Internal users can manage all booking models.

Public users can:

- Read active flows, steps, and options.
- Create booking sessions.
- Create booking answers.

Public users cannot manage backend configuration.

## Frontend Templates

OWL templates are loaded with `owl="1"`.

Component template names:

```text
booking_flow_builder.BookingRoot
booking_flow_builder.ProgressBar
booking_flow_builder.StepRenderer
booking_flow_builder.ReviewScreen
booking_flow_builder.PricingSummary
```

Frontend files:

```text
static/src/js/booking_app.js
static/src/js/components/booking_root.js
static/src/xml/booking_templates.xml
static/src/scss/booking.scss
```

## Validation Checklist

During development, the module was verified with:

```text
python -m compileall addons/booking_flow_builder
```

XML parse check:

```text
python -c "import glob, xml.etree.ElementTree as ET; [ET.parse(p) for p in glob.glob('addons/booking_flow_builder/**/*.xml', recursive=True)]; print('XML OK')"
```

Odoo install/update:

```text
docker exec odoo-booking_module-web odoo -d odoo-booking_module -i booking_flow_builder --stop-after-init --no-http --db_host=db --db_user=odoo --db_password=odoo
docker exec odoo-booking_module-web odoo -d odoo-booking_module -u booking_flow_builder --stop-after-init --no-http --db_host=db --db_user=odoo --db_password=odoo
```

Confirmed:

- `/booking/demo` returns HTTP 200.
- Flow API returns demo flow data.
- Submit API creates `booking.session`.
- PostgreSQL stores completed session, partner link, total price, and answers.
- Frontend assets are included in generated Odoo bundles.

## Current Limitations

- The Website snippet is wired to the `demo` slug by default.
- There is no editor dropdown yet for choosing a booking flow from the snippet options.
- `create_appointment` is present for future expansion but does not create calendar appointments in v1.
- Percentage pricing is calculated on the current running total in the frontend.

## Recommended Next Improvements

- Add a snippet option to select the booking flow from the Website editor.
- Add backend smart buttons from flow to sessions.
- Add date/time step support with a dedicated frontend widget.
- Add calendar event creation when `create_appointment` is enabled.
- Add configurable product selection for sale order lines.
- Add email notifications after completed booking.

