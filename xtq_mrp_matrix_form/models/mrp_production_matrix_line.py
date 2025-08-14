from odoo import models, fields, api

class MrpProductionMatrixLine(models.Model):
    _name = 'mrp.production.matrix.line'
    _description = 'Línea de Matriz de Producción Genérica'

    production_id = fields.Many2one('mrp.production', string='Orden de Producción', required=True, ondelete='cascade')
    row_value_id = fields.Many2one('product.attribute.value', string='Valor Fila', required=True)
    col_value_id = fields.Many2one('product.attribute.value', string='Valor Columna', required=True)
    product_qty = fields.Float('Cantidad Programada', default=0.0,
        help="Cantidad programada para esta combinación de atributos en la matriz.")
    qty_producing = fields.Float('Cantidad a Producir Ahora', default=0.0,
        help="Cantidad que se va a producir en este ciclo para esta combinación de atributos.")

    # El campo 'product_id' y su compute han sido eliminados por completo.
    # Esto resuelve el conflicto de guardado y el error que estás viendo.

    _sql_constraints = [
        ('unique_matrix_entry', 'unique(production_id, row_value_id, col_value_id)',
         'Cada combinación de valores de la matriz debe ser única.')
    ]