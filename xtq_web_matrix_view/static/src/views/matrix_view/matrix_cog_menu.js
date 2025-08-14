import { CogMenu } from "@web/search/cog_menu/cog_menu";

export class MatrixCogMenu extends CogMenu {
    static template = "xtq_web_matrix_view.MatrixCogMenu";
    static props = {
        ...CogMenu.props,
        hasSelectedRecords: { type: Number, optional: true },
        slots: { type: Object, optional: true },
    };
    _registryItems() {
        return this.props.hasSelectedRecords ? [] : super._registryItems();
    }
}
