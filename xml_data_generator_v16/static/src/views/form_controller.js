/** @odoo-module */

import {FormController} from "@web/views/form/form_controller";
import {useService} from "@web/core/utils/hooks";
import {patch} from "@web/core/utils/patch";
import session from "web.session";

const {useComponent, onWillStart, useEnv} = owl;

function exportRecordToXML() {
    const component = useComponent();
    const env = useEnv();
    const action = useService("action");
    return (id, model) => {
        action.doAction(
            {
                type: "ir.actions.act_window",
                name: env._t("Export to XML"),
                res_model: "xml.data.generator",
                views: [[false, "form"]],
                view_mode: "form",
                target: "new",
                context: {
                    default_res_id: id,
                    default_model_name: model,
                },
            },
            {
                onClose: async () => {
                    await component.model.load();
                    component.model.notify();
                },
            }
        );
    };
}

/**
 * 'patch' must be used to add the 'Export to XML' action to all form views
 */
patch(FormController.prototype, "xml_data_generator.export_to_xml", {
    setup() {
        this._super(...arguments);

        onWillStart(async () => {
            this.isExportEnable = await session.user_has_group("base.group_allow_export");
        });
        this.exportRecordToXML = exportRecordToXML();
    },

    /**
     * Enables the 'Export to XML' action
     */
    getActionMenuItems() {
        const menuItems = this._super(...arguments);
        if (this.isExportEnable)
            menuItems.other.push({
                key: "export_to_xml",
                description: this.env._t("Export to XML"),
                callback: this.exportRecordToXML.bind(this, this.model.root.resId, this.model.root.resModel),
            });
        return menuItems;
    },
});
