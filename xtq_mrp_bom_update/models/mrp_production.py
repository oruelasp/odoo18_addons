# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sample_bom_id = fields.Many2one(
        'mrp.bom', 
        string="Orden de Muestra (BoM Base)",
        help="BoM original que se utilizó como plantilla para la Ficha de Producción (ECO)."
    )
    
    def action_update_bom(self):
        """ 
        Hereda la función estándar para validar que si un BoM fue generado
        por un ECO, este debe estar en una etapa final (aprobado y vigente)
        para poder actualizar los componentes de la OP.
        """
        for production in self:
            if not production.bom_id:
                continue

            # Busca un ECO que haya generado la revisión actual del BoM de la OP
            eco = self.env['mrp.eco'].search([
                ('bom_ids.new_bom_id', '=', production.bom_id.id)
            ], limit=1)

            # Si existe un ECO relacionado, valida su estado
            if eco and not eco.stage_id.final_stage:
                 raise UserError(_(
                    "La Ficha de Producción (BoM: %s) vinculada a esta OP está en medio de un "
                    "proceso de cambio de ingeniería (ECO: %s) y aún no ha sido aprobada.\n\n"
                    "Por favor, complete y valide el ECO antes de actualizar los componentes."
                 ) % (production.bom_id.display_name, eco.display_name))

        return super(MrpProduction, self).action_update_bom()

    def action_create_eco(self):
        """
        Extiende la acción estándar para autocompletar el campo `sample_bom_id`
        al momento de crear un ECO desde la OP.
        """
        # Primero, ejecuta la acción estándar para obtener el diccionario de la acción
        action = super().action_create_eco()
        
        # Luego, guarda el BoM actual como el 'sample_bom_id'
        if self.bom_id:
            self.sample_bom_id = self.bom_id.id
            
        return action
