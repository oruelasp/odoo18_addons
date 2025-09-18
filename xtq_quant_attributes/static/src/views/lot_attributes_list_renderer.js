/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";
import { onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

patch(ListRenderer.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.lotAttributes = {
            headers: [],
            data: {},
        };

        onWillStart(async () => {
            // Actuar solo en el contexto de selección de lotes para un picking
            const isLotSelection = this.props.list.resModel === 'stock.quant' && 'default_product_id' in this.props.list.context;
            if (!isLotSelection) {
                return;
            }

            const productId = this.props.list.context.default_product_id;
            if (!productId) {
                return;
            }

            // Paso 1: Obtener el product.template ID desde el product.product
            const productInfo = await this.orm.read(
                "product.product",
                [productId],
                ["product_tmpl_id"]
            );
            if (!productInfo.length || !productInfo[0].product_tmpl_id) {
                return;
            }
            const templateId = productInfo[0].product_tmpl_id[0];

            // Paso 2: Verificar si la funcionalidad está activada en la plantilla del producto
            const templateData = await this.orm.read(
                "product.template",
                [templateId],
                ["show_quality_attrs_in_picking"]
            );

            if (templateData && templateData[0].show_quality_attrs_in_picking) {
                // Obtener todos los lot_ids de los registros que se van a mostrar
                const lotIds = this.props.list.records.map(rec => rec.data.lot_id[0]).filter(Boolean);

                if (lotIds.length > 0) {
                    // 2. Obtener los datos de los atributos en una sola llamada
                    const result = await this.orm.call(
                        "stock.lot",
                        "get_attributes_for_lots_view",
                        [lotIds]
                    );
                    this.lotAttributes = result;

                    // 3. Inyectar las nuevas columnas en la definición de la vista
                    this.injectAttributeColumns();
                }
            }
        });
    },

    /**
     * Añade las cabeceras de los atributos a la lista de columnas.
     */
    injectAttributeColumns() {
        if (!this.lotAttributes.headers || this.lotAttributes.headers.length === 0) {
            return;
        }

        // Crear una copia para no afectar a otras vistas
        const newColumns = [...this.props.list.archInfo.columns];

        this.lotAttributes.headers.forEach(header => {
            newColumns.push({
                // Generamos un nombre único para la columna
                name: `x_lot_attr_${header.replace(/\s+/g, '_')}`,
                string: header,
                type: 'char', // Tratamos todos los valores como texto
            });
        });
        
        // Sobrescribimos las columnas del listado
        this.props.list.archInfo.columns = newColumns;
    },

    /**
     * Procesa los datos de la fila para inyectar los valores de los atributos.
     * Esta función es llamada por el template de la vista de lista.
     */
    get cells() {
        const originalCells = super.cells;
        if (!this.lotAttributes.headers || this.lotAttributes.headers.length === 0) {
            return originalCells;
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
                };
            }
            return super.cells(record, column, index);
        };
    }
});
