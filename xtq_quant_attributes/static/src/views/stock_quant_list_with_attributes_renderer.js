/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ListRenderer } from "@web/views/list/list_renderer";
import { listView } from "@web/views/list/list_view";
import { onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class StockQuantListWithAttributesRenderer extends ListRenderer {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.state = useState({
            fieldMap: {},
        });

        onWillStart(async () => {
            if (this.props.list.context.show_lot_attributes) {
                const map = await this._fetchAttributeMap();
                this.state.fieldMap = map;
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

    get columns() {
        const originalColumns = super.columns;
        
        if (!this.props.list.context.show_lot_attributes || Object.keys(this.state.fieldMap).length === 0) {
            return originalColumns;
        }

        const fieldsToShow = new Set(Object.keys(this.state.fieldMap));
        const updatedColumns = [];

        for (const col of originalColumns) {
            if (col.name.startsWith('x_attr_')) {
                if (fieldsToShow.has(col.name)) {
                    col.string = this.state.fieldMap[col.name];
                    updatedColumns.push(col);
                }
            } else {
                updatedColumns.push(col);
            }
        }
        
        return updatedColumns;
    }
}

registry.category("views").add("stock_quant_list_with_attributes", {
    ...listView,
    Renderer: StockQuantListWithAttributesRenderer,
});
