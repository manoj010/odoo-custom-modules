/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

export class JobberDashboard extends Component {
    static template = "jobber_dashboard.Dashboard";

    setup() {
        this.action = useService("action");
        this.menu = useService("menu");
        this.state = useState({
            loading: true,
            data: {},
        });

        onWillStart(async () => {
            this.state.data = await rpc("/jobber_dashboard/data", {});
            this.state.loading = false;
        });
    }

    openAction(actionId) {
        if (actionId) {
            this.action.doAction(actionId, { clearBreadcrumbs: true });
        }
    }

    openMenu(menuId) {
        if (menuId) {
            this.menu.selectMenu(menuId);
        }
    }

    openNav(key) {
        const menuId = this.state.data.menus && this.state.data.menus[key];
        if (menuId) {
            this.openMenu(menuId);
            return;
        }

        const actionId = this.state.data.actions && this.state.data.actions[key];
        this.openAction(actionId);
    }
}

registry.category("actions").add("jobber_dashboard.dashboard", JobberDashboard);
