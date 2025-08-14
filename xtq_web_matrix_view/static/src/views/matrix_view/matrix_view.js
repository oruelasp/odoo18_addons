import { registry } from "@web/core/registry";
import { RelationalModel } from "@web/model/relational_model/relational_model";
import { MatrixArchParser } from "./matrix_arch_parser";
import { MatrixController } from "./matrix_controller";
import { MatrixRenderer } from "./matrix_renderer";

export const matrixView = {
    type: "matrix",
    Controller: MatrixController,
    Renderer: MatrixRenderer,
    ArchParser: MatrixArchParser,
    Model: RelationalModel,
    buttonTemplate: "xtq_web_matrix_view.MatrixView.Buttons",
    canOrderByCount: true,

    limit: 80,

    props: (genericProps, view) => {
        const { ArchParser } = view;
        const { arch, relatedModels, resModel } = genericProps;
        const archInfo = new ArchParser().parse(arch, relatedModels, resModel);

        return {
            ...genericProps,
            Model: view.Model,
            Renderer: view.Renderer,
            buttonTemplate: view.buttonTemplate,
            archInfo,
        };
    },
};

registry.category("views").add("matrix", matrixView);
