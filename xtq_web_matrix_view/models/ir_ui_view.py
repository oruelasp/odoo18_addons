# models/ir_ui_view.py
from odoo import fields, models

class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    type = fields.Selection(
        selection_add=[("matrix_editable", "Matrix Editable")],
        ondelete={"matrix_editable": "cascade"},
    ) 