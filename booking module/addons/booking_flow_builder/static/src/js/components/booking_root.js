/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";

export class ProgressBar extends Component {
    static template = "booking_flow_builder.ProgressBar";
}

export class PricingSummary extends Component {
    static template = "booking_flow_builder.PricingSummary";
}

export class StepRenderer extends Component {
    static template = "booking_flow_builder.StepRenderer";
}

export class ReviewScreen extends Component {
    static template = "booking_flow_builder.ReviewScreen";
}

export class BookingRoot extends Component {
    static template = "booking_flow_builder.BookingRoot";
    static components = { ProgressBar, StepRenderer, ReviewScreen, PricingSummary };
    static props = { slug: String };

    setup() {
        this.state = useState({
            loading: true,
            submitting: false,
            submitted: false,
            error: "",
            validationError: "",
            flow: null,
            activeIndex: 0,
            answers: {},
            customer: {
                name: "",
                email: "",
                phone: "",
                note: "",
            },
        });
        onWillStart(async () => this.loadFlow());
    }

    async loadFlow() {
        try {
            const result = await rpc(`/booking/api/flow/${this.props.slug}`, {});
            if (!result.success) {
                this.state.error = result.error || "This booking flow is not available.";
            } else {
                this.state.flow = result.flow;
            }
        } catch {
            this.state.error = "Unable to load this booking flow.";
        } finally {
            this.state.loading = false;
        }
    }

    get steps() {
        return this.state.flow?.steps || [];
    }

    get activeStep() {
        return this.steps[this.state.activeIndex];
    }

    get isReview() {
        return this.activeStep?.step_type === "review" || this.state.activeIndex >= this.steps.length;
    }

    get selectedAnswers() {
        return this.steps.map((step) => ({
            step,
            answer: this.state.answers[step.id],
        }));
    }

    get totalPrice() {
        let total = 0;
        for (const step of this.steps) {
            const answer = this.state.answers[step.id];
            if (!answer) {
                continue;
            }
            const optionIds = [...(answer.option_ids || [])];
            if (answer.option_id) {
                optionIds.push(answer.option_id);
            }
            for (const optionId of optionIds) {
                const option = step.options.find((item) => item.id === optionId);
                if (!option) {
                    continue;
                }
                if (option.pricing_type === "fixed") {
                    total += option.pricing_value;
                } else if (option.pricing_type === "percentage") {
                    total += total * (option.pricing_value / 100);
                }
            }
        }
        return total;
    }

    formatPrice(amount) {
        const currency = this.state.flow?.currency || {};
        const value = Number(amount || 0).toFixed(2);
        return currency.position === "after"
            ? `${value} ${currency.symbol || ""}`.trim()
            : `${currency.symbol || ""}${value}`.trim();
    }

    answerLabel(step, answer) {
        if (!answer) {
            return "";
        }
        if (answer.option_id) {
            return step.options.find((option) => option.id === answer.option_id)?.label || "";
        }
        if (answer.option_ids?.length) {
            return answer.option_ids
                .map((optionId) => step.options.find((option) => option.id === optionId)?.label)
                .filter(Boolean)
                .join(", ");
        }
        if (answer.numeric_value !== undefined && answer.numeric_value !== "") {
            return String(answer.numeric_value);
        }
        return answer.text_value || "";
    }

    setSingleChoice(stepId, optionId) {
        this.state.answers[stepId] = { step_id: stepId, option_id: optionId };
        this.state.validationError = "";
    }

    toggleMultiChoice(stepId, optionId) {
        const answer = this.state.answers[stepId] || { step_id: stepId, option_ids: [] };
        const selected = new Set(answer.option_ids || []);
        selected.has(optionId) ? selected.delete(optionId) : selected.add(optionId);
        this.state.answers[stepId] = { step_id: stepId, option_ids: [...selected] };
        this.state.validationError = "";
    }

    setTextAnswer(stepId, value) {
        this.state.answers[stepId] = { step_id: stepId, text_value: value };
        this.state.validationError = "";
    }

    setNumberAnswer(stepId, value) {
        this.state.answers[stepId] = { step_id: stepId, numeric_value: value };
        this.state.validationError = "";
    }

    setCustomer(field, value) {
        this.state.customer[field] = value;
        this.state.validationError = "";
    }

    validateStep(step = this.activeStep) {
        if (!step || step.step_type === "info" || step.step_type === "review" || !step.required) {
            return true;
        }
        const answer = this.state.answers[step.id];
        const hasChoice = Boolean(answer?.option_id || answer?.option_ids?.length);
        const hasText = Boolean((answer?.text_value || "").trim());
        const hasNumber = answer?.numeric_value !== undefined && answer.numeric_value !== "";
        if (["single_choice", "multi_choice"].includes(step.step_type) && !hasChoice) {
            this.state.validationError = "Please choose an option to continue.";
            return false;
        }
        if (["text", "textarea"].includes(step.step_type) && !hasText) {
            this.state.validationError = "Please fill in this field to continue.";
            return false;
        }
        if (step.step_type === "number" && !hasNumber) {
            this.state.validationError = "Please enter a number to continue.";
            return false;
        }
        return true;
    }

    next() {
        if (!this.validateStep()) {
            return;
        }
        this.state.validationError = "";
        this.state.activeIndex = Math.min(this.state.activeIndex + 1, this.steps.length);
    }

    back() {
        this.state.validationError = "";
        this.state.activeIndex = Math.max(this.state.activeIndex - 1, 0);
    }

    validateCustomer() {
        if (!this.state.customer.name.trim() || !this.state.customer.email.trim()) {
            this.state.validationError = "Please add your name and email before submitting.";
            return false;
        }
        return true;
    }

    async submit() {
        if (!this.validateCustomer()) {
            return;
        }
        this.state.submitting = true;
        this.state.validationError = "";
        try {
            const answers = Object.values(this.state.answers);
            const result = await rpc("/booking/api/submit", {
                flow_id: this.state.flow.id,
                answers,
                total_price: this.totalPrice,
                customer_name: this.state.customer.name,
                customer_email: this.state.customer.email,
                customer_phone: this.state.customer.phone,
                customer_note: this.state.customer.note,
            });
            if (result.success) {
                this.state.submitted = true;
            } else {
                this.state.validationError = result.error || "Could not submit this booking.";
            }
        } catch {
            this.state.validationError = "Could not submit this booking.";
        } finally {
            this.state.submitting = false;
        }
    }
}
