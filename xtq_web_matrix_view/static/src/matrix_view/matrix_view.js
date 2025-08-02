// static/src/matrix_view/matrix_view.js
/** @odoo-module **/

import { registry } from "@web/core/registry";
import { AbstractView } from "@web/views/abstract_view";
import { useService } from "@web/core/utils/hooks";
import { Layout } from "@web/search/layout";
import { useModel } from "@web/views/model";
import { Component, onWillStart, useState } from "@odoo/owl";

class MatrixModel extends AbstractModel {
    async load(searchParams) {
        this.get_data_route = this.props.arch.attrs.get_data_route;
        if (!this.get_data_route) {
            this.matrixData = { is_empty: true, message: "El atributo 'get_data_route' es requerido en el arch de la vista matriz." };
            return;
        }
        this.matrixData = await this.rpc(this.get_data_route, { domain: searchParams.domain });
        this.initialData = JSON.parse(JSON.stringify(this.matrixData));
    }

    getDirtyData() {
        // Lógica para devolver solo los datos que han cambiado
        const dirtyData = {};
        // ... (Implementación de comparación entre this.matrixData y this.initialData)
        return dirtyData;
    }
}

class MatrixRenderer extends Component {
    static template = "xtq_web_matrix_view.MatrixView";
}

class MatrixController extends AbstractController {
    setup() {
        super.setup();
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        this.model = useModel(this.props.Model, this.props.modelParams);
    }
    
    async onSave() {
        const saveRoute = this.props.arch.attrs.save_route;
        if (!saveRoute) {
            this.notification.add("Ruta de guardado no definida.", { type: "danger" });
            return;
        }
        
        const dirtyData = this.model.getDirtyData();
        if (Object.keys(dirtyData).length === 0) {
            this.notification.add("No hay cambios que guardar.", { type: "warning" });
            return;
        }
        const success = await this.rpc(saveRoute, { matrix_data: dirtyData });
        if (success) {
            this.notification.add("Cambios guardados.", { type: "success" });
            await this.model.load(this.props.searchMenu.domain);
        }
    }
}

MatrixController.components = { Layout, MatrixRenderer };

export const matrixEditableView = {
    type: "matrix_editable",
    display_name: "Matriz Editable",
    icon: "fa-th",
    multiRecord: true,
    Controller: MatrixController,
    Model: MatrixModel,
    props: (genericProps, view) => {
        const { arch } = view;
        return {
            ...genericProps,
            Model: MatrixModel,
            modelParams: { arch },
            Renderer: MatrixRenderer,
            rendererProps: { arch },
        };
    },
};

registry.category("views").add("matrix_editable", matrixEditableView); 