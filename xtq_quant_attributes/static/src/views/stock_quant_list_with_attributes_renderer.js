/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ListRenderer } from "@web/views/list/list_renderer";
import { listView } from "@web/views/list/list_view";
import { onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class StockQuantListWithAttributesRenderer extends ListRenderer {
    setup() {
        super.setup();
        this.orm = useService("orm");

        onWillStart(async () => {
            if (this.props.list.context.show_lot_attributes) {
                const fieldMap = await this._fetchAttributeMap();
                if (Object.keys(fieldMap).length > 0) {
                    this._updateColumns(fieldMap);
                }
            }
        });
    }

    async _fetchAttributeMap() {
        const productId = this.props.list.context.lot_attributes_product_id;
        if (!productId) {
            return {};
        }
        return await this.orm.call(
            'stock.quant',
            'get_attribute_field_map',
            [productId]
        );
    }

    _updateColumns(fieldMap) {
        const fieldsToShow = new Set(Object.keys(fieldMap));
        
        // Modificar directamente el array de columnas en las props.
        // En onWillStart, este objeto es mutable.
        const columns = this.props.list.columns;
        const finalColumns = [];

        for (const col of columns) {
            if (col.name.startsWith('x_attr_')) {
                if (fieldsToShow.has(col.name)) {
                    col.string = fieldMap[col.name];
                    finalColumns.push(col);
                }
            } else {
                finalColumns.push(col);
            }
        }

        this.props.list.columns = finalColumns;
    }
}

registry.category("views").add("stock_quant_list_with_attributes", {
    ...listView,
    Renderer: StockQuantListWithAttributesRenderer,
});
