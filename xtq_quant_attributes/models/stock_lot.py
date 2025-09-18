# -*- coding: utf-8 -*-
from odoo import api, models

class StockLot(models.Model):
    _inherit = 'stock.lot'

    @api.model
    def get_attributes_for_lots_view(self, lot_ids):
        """
        Consulta y estructura los atributos de calidad para una lista de lotes.
        Este método está diseñado para ser llamado desde el frontend (JS).

        :param lot_ids: Lista de IDs de stock.lot.
        :return: Diccionario JSON con 'headers' y 'data' para la vista.
        """
        if not lot_ids:
            return {'headers': [], 'data': {}}

        # 1. Identificar los atributos que son de lote
        lot_attributes = self.env['product.attribute'].search([('is_lot_attribute', '=', True)])
        if not lot_attributes:
            return {'headers': [], 'data': {}}

        headers = lot_attributes.mapped('name')

        # 2. Consultar todas las líneas de atributos para los lotes dados
        attribute_lines = self.env['stock.lot.attribute.line'].search([
            ('lot_id', 'in', lot_ids),
            ('attribute_id', 'in', lot_attributes.ids)
        ])

        # 3. Procesar y estructurar los datos para el frontend
        data = {lot_id: {} for lot_id in lot_ids}
        for line in attribute_lines:
            lot_id = line.lot_id.id
            attr_name = line.attribute_id.name
            # Formatear el valor. Asume que es un campo de texto o seleccion.
            # Se puede mejorar para manejar diferentes tipos de datos si es necesario.
            value = line.value_id.name if line.value_id else ''
            data[lot_id][attr_name] = value

        return {
            'headers': headers,
            'data': data,
        }
