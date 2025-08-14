from odoo import models, fields, api

class MrpProductionMatrixLine(models.Model):
    _name = 'mrp.production.matrix.line'
    _description = 'Línea de Matriz de Producción Genérica'

    production_id = fields.Many2one('mrp.production', string='Orden de Producción', required=True, ondelete='cascade')
    row_value_id = fields.Many2one('product.attribute.value', string='Valor Fila', required=True)
    col_value_id = fields.Many2one('product.attribute.value', string='Valor Columna', required=True)
    quantity = fields.Float('Cantidad', default=0.0)

    # El campo 'product_id' y su compute han sido eliminados por completo.
    # Esto resuelve el conflicto de guardado y el error que estás viendo.

    _sql_constraints = [
        ('unique_matrix_entry', 'unique(production_id, row_value_id, col_value_id)',
         'Cada combinación de valores de la matriz debe ser única.')
    ]