odoo.define("xml_data_generator.FormController", function (require) {
    "use strict";

    const FormController = require("web.FormController");
    const {patch} = require("web.utils");
    const session = require("web.session");
    var core = require("web.core");
    var _t = core._t;

    /**
     * 'patch' must be used to add the 'Export to XML' action to all form views
     */
    patch(FormController.prototype, "xml_data_generator.export_to_xml", {
        /**
         * Checks if current user has export permissions on current model
         */
        willStart() {
            const sup = this._super(...arguments);
            const acl = session.user_has_group("base.group_allow_export").then((hasGroup) => {
                this.isExportEnable = hasGroup;
            });
            return Promise.all([sup, acl]);
        },

        /**
         * Enables the 'Export to XML' action
         */
        _getActionMenuItems() {
            var menuItems = this._super(...arguments);

            if (!menuItems?.items.other.length || !this.isExportEnable) return menuItems;
            menuItems.items.other.push({
                description: _t("Export to XML"),
                callback: () => {
                    this.do_action({
                        type: "ir.actions.act_window",
                        name: _t("Export to XML"),
                        res_model: "xml.data.generator",
                        views: [[false, "form"]],
                        view_mode: "form",
                        target: "new",
                        context: {
                            default_res_id: this.controlPanelProps.actionMenus.activeIds[0],
                            default_model_name: this.model.loadParams.modelName,
                        },
                    });
                },
            });
            return menuItems;
        },
    });
});
