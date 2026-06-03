/** @odoo-module **/

export function getKathmanduTime() {
    return new Date().toLocaleTimeString("en-US", {
        timeZone: "Asia/Kathmandu",
        hour12: true,
        hour: "numeric",
        minute: "2-digit",
        second: "2-digit"
    });
}
