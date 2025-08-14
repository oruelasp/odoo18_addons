from odoo import fields, models


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    type = fields.Selection(
        selection_add=[("matrix", "Matrix Editable")],
        ondelete={"matrix": "cascade"},
    )

    def _get_view_info(self):
        res = super()._get_view_info()
        res["matrix"] = {"icon": "oi oi-text-wrap"}
        return res
