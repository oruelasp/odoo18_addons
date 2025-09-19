/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ListRenderer } from "@web/views/list/list_renderer";
import { useState, onWillStart, onWillUpdateProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * Heredamos del ListRenderer estándar para crear nuestro propio componente especializado.
 * Este renderer solo se usará en las vistas que lo declaren explícitamente con js_class.
 */
export class LotAttributeListRenderer extends ListRenderer {
    setup() {
        super.setup();
        this.orm = useService("orm");
        
        this.state = useState({
            qualityColumns: [], // Almacena solo nuestras columnas dinámicas.
        });
        
        this.baseColumns = null; 
        this.lotAttributes = { headers: [], data: {} };
        this.attributesFetched = false;

        const fetchData = async (list) => {
            if (this.attributesFetched || list.records.length === 0) {
                return;
            }
            this.attributesFetched = true;

            // Estrategia definitiva: Obtenemos el product_id directamente del primer
            // registro de la lista. Esta es la fuente de verdad más fiable,
            // ya que no depende del contexto.
            const firstRecord = list.records[0];
            if (!firstRecord.data.product_id || !firstRecord.data.product_id.length) {
                return;
            }
            const productId = firstRecord.data.product_id[0];
            
            // Con el product_id, continuamos el flujo que ya conocemos.
            const productInfo = await this.orm.read("product.product", [productId], ["product_tmpl_id"]);
            if (!productInfo.length || !productInfo[0].product_tmpl_id) { return; }
            const templateId = productInfo[0].product_tmpl_id[0];

            const templateData = await this.orm.read("product.template", [templateId], ["show_quality_attrs_in_picking"]);

            if (templateData && templateData[0].show_quality_attrs_in_picking) {
                const lotIds = list.records.map(rec => rec.data.lot_id[0]).filter(Boolean);

                if (lotIds.length > 0) {
                    const result = await this.orm.call("stock.lot", "get_attributes_for_lots_view", [lotIds]);
                    this.lotAttributes = result;
                    
                    const newQualityColumns = [];
                    this.lotAttributes.headers.forEach(header => {
                        newQualityColumns.push({
                            name: `x_lot_attr_${header.replace(/\s+/g, '_')}`,
                            string: header,
                            type: 'char',
                        });
                    });
                    
                    this.state.qualityColumns = newQualityColumns;
                }
            }
        };

        onWillStart(() => fetchData(this.props.list));
        onWillUpdateProps((nextProps) => fetchData(nextProps.list));
    }

    get columns() {
        const base = this.baseColumns || this.props.list.archInfo.columns;
        return [...base, ...this.state.qualityColumns];
    }
    
    set columns(newColumns) {
        this.baseColumns = newColumns ? [...newColumns] : [];
    }

    get cells() {
        const originalCellsGetter = super.cells;
        if (!this.state.qualityColumns.length) {
            return originalCellsGetter;
        }

        return (record, column, index) => {
            const lotId = record.data.lot_id ? record.data.lot_id[0] : null;
            if (lotId && column.name.startsWith('x_lot_attr_')) {
                const attrName = column.string;
                const lotData = this.lotAttributes.data[lotId];
                const value = lotData && lotData[attrName] ? lotData[attrName] : '';
                
                return {
                    ...column,
                    value: value,
                    formattedValue: value,
                    props: { ...column.props, readonly: true },
                };
            }
            return originalCellsGetter(record, column, index);
        };
    }
}

// 1. Registramos nuestro renderer personalizado para que Odoo lo conozca.
registry.category("renderers").add("lot_attribute_list_renderer", {
    Component: LotAttributeListRenderer,
    target: "list",
});

// 2. Importamos la vista de lista base para poder heredar de ella.
import { listView } from "@web/views/list/list_view";

// 3. Creamos una nueva definición de vista que utiliza nuestro renderer.
export const lotAttributeListView = {
    ...listView,
    Renderer: LotAttributeListRenderer,
};

// 4. Registramos esta nueva VISTA en el registro de vistas.
// Ahora, cuando el XML use js_class="lot_attribute_list_renderer", encontrará esta definición.
registry.category("views").add("lot_attribute_list_renderer", lotAttributeListView);
