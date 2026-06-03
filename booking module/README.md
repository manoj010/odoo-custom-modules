# Custom Odoo Modules

This repository contains custom Odoo 18 addons.

## Included Modules

### booking_flow_builder

`booking_flow_builder` is a no-code booking flow builder for Odoo Website.

It lets internal users create booking flows with ordered steps and options, then lets public website visitors complete those flows at URLs such as:

```text
/booking/demo
/booking/<your-flow-slug>
```

The module saves completed bookings as `booking.session` records with customer details, selected answers, selected options, calculated total price, linked partner, and optional sale order.

Full documentation is available in:

[addons/booking_flow_builder/README.md](addons/booking_flow_builder/README.md)

