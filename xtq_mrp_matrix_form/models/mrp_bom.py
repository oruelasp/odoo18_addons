# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MrpBom(models.Model):
    """
    Extiende la Lista de Materiales (LdM) para añadir configuración de matriz
    que definirá los ejes de atributos a usar en las Órdenes de Producción.
    """
    _inherit = 'mrp.bom'

    matrix_attribute_row_id = fields.Many2one(
        'product.attribute',
        string='Atributo Fila (Matriz)',
        help="Define el atributo que se usará para las filas (eje X) en la matriz de producción."
    )
    matrix_attribute_col_id = fields.Many2one(
        'product.attribute',
        string='Atributo Columna (Matriz)',
        help="Define el atributo que se usará para las columnas (eje Y) en la matriz de producción."
    )

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id_set_matrix_attributes(self):
        """
        Al cambiar el producto de la LdM, hereda la configuración de atributos
        de la matriz definida en la plantilla del producto.
        AC1 de HU-MRP-004.
        """
        if self.product_tmpl_id:
            self.matrix_attribute_row_id = self.product_tmpl_id.matrix_attribute_x_id.id
            self.matrix_attribute_col_id = self.product_tmpl_id.matrix_attribute_y_id.id

class MrpBomLine(models.Model):
    """
    Extiende las líneas de la LdM para permitir especificar a qué valores de
    atributos de la matriz aplica cada componente.
    """
    _inherit = 'mrp.bom.line'

    matrix_row_value_ids = fields.Many2many(
        'product.attribute.value',
        'mrp_bom_line_row_attr_val_rel',
        'bom_line_id', 'attribute_value_id',
        string='AtributosFila Aplicables',
        help="Especifica para qué valores del atributo de Fila aplica este componente. Si está vacío, aplica a todos."
    )
    matrix_col_value_ids = fields.Many2many(
        'product.attribute.value',
        'mrp_bom_line_col_attr_val_rel',
        'bom_line_id', 'attribute_value_id',
        string='Atributos Columna Aplicables',
        help="Especifica para qué valores del atributo de Columna aplica este componente. Si está vacío, aplica a todos."
    )
