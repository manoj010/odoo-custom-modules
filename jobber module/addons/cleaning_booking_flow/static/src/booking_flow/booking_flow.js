/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { mountComponent } from "@web/env";
import { rpc } from "@web/core/network/rpc";

const MONTH_DAYS = [
    ["Sun", "01", "2026-05-01"],
    ["Mon", "02", "2026-05-02"],
    ["Tue", "03", "2026-05-03"],
    ["Wed", "04", "2026-05-04"],
    ["Thu", "05", "2026-05-05"],
    ["Fri", "06", "2026-05-06"],
    ["Sat", "07", "2026-05-07"],
    ["Sun", "08", "2026-05-08"],
    ["Mon", "09", "2026-05-09"],
    ["Tue", "10", "2026-05-10"],
    ["Wed", "11", "2026-05-11"],
    ["Thu", "12", "2026-05-12"],
    ["Fri", "13", "2026-05-13"],
    ["Sat", "14", "2026-05-14"],
    ["Sun", "15", "2026-05-15"],
    ["Mon", "16", "2026-05-16"],
    ["Tue", "17", "2026-05-17"],
    ["Wed", "18", "2026-05-18"],
    ["Thu", "19", "2026-05-19"],
    ["Fri", "20", "2026-05-20"],
    ["Sat", "21", "2026-05-21"],
    ["Sun", "22", "2026-05-22"],
    ["Mon", "23", "2026-05-23"],
    ["Tue", "24", "2026-05-24"],
    ["Wed", "25", "2026-05-25"],
    ["Thu", "26", "2026-05-26"],
    ["Fri", "27", "2026-05-27"],
    ["Sat", "28", "2026-05-28"],
    ["Sun", "29", "2026-05-29"],
    ["Mon", "30", "2026-05-30"],
    ["Tue", "31", "2026-05-31"],
    ["Wed", "01", "2026-06-01", true],
    ["Thu", "02", "2026-06-02", true],
    ["Fri", "03", "2026-06-03", true],
];

const TIMES = ["09:00 AM", "12:00 PM", "02:00 PM", "04:00 PM", "06:00 PM", "08:00 PM"];

class Summary extends Component {
    static template = "cleaning_booking_flow.Summary";
    static props = {
        selectedService: { optional: true },
        selectedDateLabel: { optional: true },
        selectedTime: { optional: true },
    };
}

export class CleaningBookingFlow extends Component {
    static template = "cleaning_booking_flow.CleaningBookingFlow";
    static components = { Summary };

    setup() {
        this.state = useState({
            isOpen: false,
            step: 1,
            services: [],
            selectedService: null,
            selectedDate: null,
            selectedDateLabel: "",
            selectedTime: null,
            customer: {
                name: "",
                email: "",
                phone: "",
                location: "",
                message: "",
            },
            paymentMethod: "pay_later",
            bookingId: null,
            loading: false,
            error: null,
        });
        this.days = MONTH_DAYS;
        this.weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
        this.times = TIMES;
        window.cleaningBookingFlow = this;

        onWillStart(async () => {
            await this.fetchServices();
        });
    }

    get progressWidth() {
        return `${(this.state.step / 5) * 100}%`;
    }

    get title() {
        return [
            "",
            "Select the Service You Need",
            "Schedule Your Booking",
            "Complete Your Details",
            "Confirm Your Payment",
            "Booking Confirmed",
        ][this.state.step];
    }

    get subtitle() {
        return [
            "",
            "Select a service to get started with expert support.",
            "Select a convenient date and time for your appointment.",
            "Enter your contact details to proceed with the booking.",
            "Proceed with payment to finalize your appointment.",
            "Your cleaning service has been successfully booked.",
        ][this.state.step];
    }

    async fetchServices() {
        try {
            const services = await rpc("/cleaning-booking/services", {});
            this.state.services = services;
            if (!services.length) {
                this.state.error = "No cleaning services are available yet.";
            }
        } catch {
            this.state.error = "We could not load services. Please try again.";
        }
    }

    open() {
        this.state.isOpen = true;
        document.body.classList.add("o_cleaning_booking_locked");
    }

    close() {
        this.state.isOpen = false;
        document.body.classList.remove("o_cleaning_booking_locked");
    }

    reset() {
        this.state.step = 1;
        this.state.selectedService = null;
        this.state.selectedDate = null;
        this.state.selectedDateLabel = "";
        this.state.selectedTime = null;
        this.state.customer.name = "";
        this.state.customer.email = "";
        this.state.customer.phone = "";
        this.state.customer.location = "";
        this.state.customer.message = "";
        this.state.paymentMethod = "pay_later";
        this.state.bookingId = null;
        this.state.error = null;
    }

    back() {
        if (this.state.step <= 1) {
            this.close();
            return;
        }
        this.state.step -= 1;
        this.state.error = null;
    }

    async next() {
        this.state.error = null;
        if (!this.validateStep()) {
            return;
        }
        if (this.state.step === 4) {
            await this.submitBooking();
            return;
        }
        if (this.state.step < 5) {
            this.state.step += 1;
        }
    }

    validateStep() {
        if (this.state.step === 1 && !this.state.selectedService) {
            this.state.error = "Please select a service.";
            return false;
        }
        if (this.state.step === 2 && (!this.state.selectedDate || !this.state.selectedTime)) {
            this.state.error = "Please select a date and time.";
            return false;
        }
        if (this.state.step === 3) {
            const customer = this.state.customer;
            if (!customer.name.trim() || !customer.email.trim() || !customer.phone.trim()) {
                this.state.error = "Please enter your name, email, and phone.";
                return false;
            }
        }
        return true;
    }

    selectService(service) {
        this.state.selectedService = service;
        this.state.error = null;
    }

    selectDate(day) {
        this.state.selectedDate = day[2];
        this.state.selectedDateLabel = `${day[1]} MAY, 2026`;
        this.state.error = null;
    }

    selectTime(time) {
        this.state.selectedTime = time;
        this.state.error = null;
    }

    updateCustomer(field, ev) {
        this.state.customer[field] = ev.target.value;
    }

    async submitBooking() {
        this.state.loading = true;
        try {
            const result = await rpc("/cleaning-booking/create", {
                service_id: this.state.selectedService.id,
                customer_name: this.state.customer.name,
                email: this.state.customer.email,
                phone: this.state.customer.phone,
                location: this.state.customer.location,
                message: this.state.customer.message,
                booking_date: this.state.selectedDate,
                booking_time: this.state.selectedTime,
                price: this.state.selectedService.price,
            });
            if (!result.success) {
                this.state.error = result.message || "We could not create this booking.";
                return;
            }
            this.state.bookingId = result.booking_id;
            this.state.step = 5;
        } catch {
            this.state.error = "We could not create this booking. Please try again.";
        } finally {
            this.state.loading = false;
        }
    }
}

function wireBookingButtons() {
    if (document.body.dataset.cleaningBookingClickBound) {
        return;
    }
    document.body.dataset.cleaningBookingClickBound = "1";
    document.addEventListener("click", (ev) => {
        const trigger = ev.target.closest(".js_open_cleaning_booking");
        if (!trigger) {
            return;
        }
        ev.preventDefault();
        const flow = window.cleaningBookingFlow;
        if (flow) {
            flow.open();
        }
    });
}

async function startCleaningBookingFlow() {
    wireBookingButtons();
    let target = document.querySelector("#cleaning_booking_flow_mount");
    if (!target) {
        target = document.createElement("div");
        target.id = "cleaning_booking_flow_mount";
        document.body.appendChild(target);
    }
    if (!target || target.dataset.cleaningBookingMounted) {
        return;
    }
    target.dataset.cleaningBookingMounted = "1";
    await mountComponent(CleaningBookingFlow, target);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startCleaningBookingFlow);
} else {
    startCleaningBookingFlow();
}
