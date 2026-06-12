# Sparkle Booking Flow

This Odoo 18 addon adds a full-screen website booking flow for cleaning services. It is independent from the existing Jobber/service CRM addon and can be installed alongside it.

## What It Adds

- A website overlay booking flow opened by any button or link with the class `js_open_sparkle_booking`.
- Admin-managed service options shown on the first booking step.
- Admin-managed weekly availability rules used by the calendar step.
- A backend app menu named `Sparkle Booking`.
- Two backend models:
- `sparkle.booking.service` for service choices.
- `sparkle.booking.availability` for service availability rules.
- `sparkle.booking` for submitted bookings.
- Public JSON routes for loading services and creating bookings.
- A mock payment step that saves bookings with `payment_status = pending`.

## User Flow

1. A visitor clicks a website button with `.js_open_sparkle_booking`.
2. The overlay slides up over the current page.
3. The visitor selects a service.
4. The visitor selects today or a future date.
5. Odoo returns available time slots for that service/date.
5. The visitor enters contact details.
6. The visitor confirms the mock payment step.
7. Odoo creates a `sparkle.booking` record.
8. The success screen appears.
9. The visitor clicks `Finish` and is redirected to `/`.

## Adding A Book Now Button

Use this on any website page:

```html
<a href="#" class="btn btn-primary js_open_sparkle_booking">Book Now</a>
```

The `href="#"` is fine because the frontend JavaScript prevents the default link action and opens the overlay.

If you are writing template code directly, a button is also valid:

```html
<button type="button" class="btn btn-primary js_open_sparkle_booking">Book Now</button>
```

## Admin Service Options

Go to:

```text
Sparkle Booking -> Service Options
```

Admins can create, edit, archive, reorder, or delete service options. Active services appear dynamically in the website booking flow.

Service fields:

- `Name`: Display name shown to visitors.
- `Description`: Short description shown under the service name.
- `Icon Class`: Font Awesome class, for example `fa fa-tint`.
- `Price`: Used on the payment confirmation step.
- `Duration Minutes`: Stored for future scheduling integrations.
- `Active`: Only active services are shown on the website.
- `Sequence`: Controls display order.

## Admin Availability

Go to:

```text
Sparkle Booking -> Availability
```

Admins can create weekly availability rules for each service.

Availability fields:

- `Service`: Service this availability applies to.
- `Weekday`: Day of week for the rule.
- `Start Time`: Start of the available window.
- `End Time`: End of the available window.
- `Slot Interval Minutes`: Gap between generated appointment slots.
- `Active`: Only active rules are used by the website calendar.

Example:

```text
Carpet & Upholstery Cleaning
Monday
09:00 - 18:00
60 minute slots
```

If no availability rules exist for a service/date yet, the website route falls back to sample slots so the flow still works while admins configure rules.

The calendar never allows dates before today. The backend also rejects past dates, so this rule is protected even if someone bypasses the frontend.

## Default Services

The module seeds six default services during first install only:

- Carpet & Upholstery Cleaning
- Water Damage Restoration
- End Of Lease Cleaning
- Commercial Premises Cleaning
- Mould Removal & Remediation
- Builders & Post-Reno Cleaning

These are normal database records after install. They can be edited or deleted by an admin.

The defaults are created in `hooks.py` through `post_init_hook`. They are only created when there are no existing `sparkle.booking.service` records.

## Booking Records

Submitted bookings are stored under:

```text
Sparkle Booking -> Bookings
```

The booking stores:

- Selected service
- Customer name
- Email
- Phone
- Location
- Optional message
- Booking date
- Booking time
- Price
- Payment status
- Booking state
- Internal notes

New website bookings are created as:

```text
state = confirmed
payment_status = pending
```

## Frontend Files

The overlay lives in:

```text
static/src/booking_flow/
```

Important files:

- `booking_flow.js`: OWL component state, validation, route calls, open/close behavior, and finish redirect.
- `booking_flow.xml`: OWL templates for all five steps.
- `booking_flow.scss`: Overlay styling matching the reference booking screenshots.

The frontend assets are loaded through `web.assets_frontend` in `__manifest__.py`.

## Website Mount Point

The module injects this container into `website.layout`:

```html
<div id="sparkle_booking_flow_mount"></div>
```

The JavaScript also creates a fallback mount container if the layout container is not found.

## JSON Routes

### `/sparkle-booking/services`

Type: JSON  
Auth: public

Returns active services ordered by sequence.

Example response shape:

```json
[
  {
    "id": 1,
    "name": "Carpet & Upholstery Cleaning",
    "description": "Professional steam and dry cleaning.",
    "icon_class": "fa fa-object-group",
    "price": 45.0,
    "duration_minutes": 90
  }
]
```

### `/sparkle-booking/availability`

Type: JSON  
Auth: public

Input:

```json
{
  "service_id": 1,
  "date": "2026-06-12"
}
```

Returns available slots for that service/date and excludes already-booked times:

```json
{
  "success": true,
  "slots": ["09:00 AM", "10:00 AM", "11:00 AM"]
}
```

### `/sparkle-booking/create`

Type: JSON  
Auth: public  
CSRF: disabled for website JSON submission

Required:

- `service_id`
- `customer_name`
- `email`
- `phone`

Optional:

- `location`
- `message`
- `booking_date`
- `booking_time`
- `price`

Creates a confirmed booking and returns:

```json
{
  "success": true,
  "booking_id": 1,
  "message": "Your cleaning service has been successfully booked."
}
```

## Updating After Code Changes

For this Docker setup, update the module with:

```powershell
docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d odoo-jobber_module-db -u sparkle_booking_flow --db_host=db --db_user=odoo --db_password=odoo --stop-after-init
```

Then refresh the website page. If browser assets look stale, use a hard refresh.

## Future Integration Points

This module is intentionally simple for the first version. Later it can integrate with:

- Odoo Calendar: create calendar events for confirmed bookings.
- Odoo Appointment: replace the static date/time grid with real availability.
- CRM: create or link leads/opportunities from bookings.
- Sales: create sale orders or quotations using the selected service price.
- Payment Providers: replace mock payment with real provider transactions.
- Mail/SMS: send confirmation messages after booking creation.
