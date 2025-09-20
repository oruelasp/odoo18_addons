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
            // Solo ejecutar si estamos en la vista correcta
            if (this.props.list.context.show_lot_attributes) {
                await this._fetchAttributeMap();
            }
        });
    }

    get list() {
        const list = super.list;
        // Solo modificar columnas si tenemos un mapa de atributos
        if (this.props.list.context.show_lot_attributes && Object.keys(this.state.fieldMap).length > 0) {
            list.columns = this.getUpdatedColumns(list.columns);
        }
        return list;
    }

    async _fetchAttributeMap() {
        const productId = this.props.list.context.lot_attributes_product_id;
        if (!productId) {
            this.state.fieldMap = {};
            return;
        }
        const map = await this.orm.call(
            'stock.quant',
            'get_attribute_field_map',
            [productId]
        );
        this.state.fieldMap = map;
    }

    getUpdatedColumns(columns) {
        // Usamos un Set para una búsqueda más eficiente de los campos a mantener
        const fieldsToShow = new Set(Object.keys(this.state.fieldMap));
        
        const updatedColumns = [];
        for (const col of columns) {
            if (col.name.startsWith('x_attr_')) {
                // Si el campo genérico está en nuestro mapa, lo mostramos y actualizamos su etiqueta
                if (fieldsToShow.has(col.name)) {
                    col.string = this.state.fieldMap[col.name];
                    updatedColumns.push(col);
                }
                // Si no está en el mapa, se omite y por tanto se oculta
            } else {
                // Es una columna estándar, la mantenemos
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
