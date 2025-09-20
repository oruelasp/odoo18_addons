/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ListRenderer } from "@web/views/list/list_renderer";
import { listView } from "@web/views/list/list_view";
import { onWillStart, onWillUpdateProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class StockQuantListWithAttributesRenderer extends ListRenderer {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.fieldMap = null; // {'x_attr_1': 'Tono', ...}

        onWillStart(async () => {
            if (this.props.list?.context?.show_lot_attributes) {
                this.fieldMap = await this._fetchAttributeMap();
                this._updateColumns(this.props);
            }
        });

        onWillUpdateProps(async (nextProps) => {
            if (!nextProps.list?.context?.show_lot_attributes) {
                return;
            }
            if (!this.fieldMap) {
                this.fieldMap = await this._fetchAttributeMap(nextProps);
            }
            this._updateColumns(nextProps);
        });
    }

    async _fetchAttributeMap(props = this.props) {
        const productId = props.list?.context?.lot_attributes_product_id;
        if (!productId) {
            return {};
        }
        return await this.orm.call(
            "stock.quant",
            "get_attribute_field_map",
            [productId]
        );
    }

    _updateColumns(props = this.props) {
        if (!this.fieldMap || Object.keys(this.fieldMap).length === 0) return;

        const archInfo = props.archInfo;
        if (!archInfo || !Array.isArray(archInfo.columns)) return;

        const cols = archInfo.columns;
        const fieldsToShow = new Set(Object.keys(this.fieldMap));

        for (const col of cols) {
            if (!col || typeof col.name !== "string") continue;
            if (col.name.startsWith("x_attr_")) {
                if (fieldsToShow.has(col.name)) {
                    // Odoo 18 usa 'label' para el texto de cabecera
                    col.label = this.fieldMap[col.name];
                    col.optional = false;
                    // limpiar invisibilidad si la tuviera
                    if (col.invisible) delete col.invisible;
                } else {
                    col.optional = "hide";
                }
            }
        }
    }
}

registry.category("views").add("stock_quant_list_with_attributes", {
    ...listView,
    Renderer: StockQuantListWithAttributesRenderer,
});
