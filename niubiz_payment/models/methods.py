import logging
import base64
import json
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    is_niubiz = fields.Boolean('Es niubiz')
    niubiz_transaction = fields.Binary('Niubiz transaccion')
    niubiz_transaction_msg = fields.Char('Niubiz transacción')
    niubiz_countable = fields.Boolean('Niubiz contable')
    niubiz_amount = fields.Monetary('Niubiz monto')
    niubiz_cancel = fields.Char('Niubiz cancelacion')
    niubiz_cancel_state = fields.Boolean('Niubiz cancelacion estado')
    niubiz_confirm = fields.Char('Niubiz confirmacion')
    niubiz_confirm_state = fields.Boolean('Niubiz confirmacion estado')
    niubiz_state = fields.Char(string='Estado niubiz', compute='_compute_niubiz_state')

    def _compute_niubiz_state(self):
        for rec in self:
            if rec.niubiz_countable:
                rec.niubiz_state = "Confirmada Contable"
            else:
                if rec.niubiz_confirm_state:
                    rec.niubiz_state = "Confirmada"
                else:
                    rec.niubiz_state = "Por Confirmar"

            if rec.state == "cancel":
                if rec.niubiz_cancel_state:
                    rec.niubiz_state = "Cancelado"
                else:
                    rec.niubiz_state = "Por Cancelar"

    def action_confirm_niubiz(self):
        if not self.is_niubiz:
            raise ValidationError(_("Esta venta no fue procesada con niubiz."))

        if self.niubiz_countable:
            raise ValidationError(_("Esta venta no necesita confirmacion."))

        days = abs((datetime.today() - self.create_date).days)
        if days > 7:
            msg = f"Se superó la cantidad de días para confirmar este pedido. {days} "
            self.write({
                'niubiz_confirm_state': msg,
                'niubiz_confirm': False
            })
            raise ValidationError(_(msg))
        current_amount = self.niubiz_amount
        new_amount = self.amount_total
        percent_variation = ((new_amount - current_amount) / current_amount) * 100.0
        if percent_variation > 10:
            msg = f"La variación de monto no es correcta "
            self.write({
                'niubiz_confirm': msg,
                'niubiz_confirm_state': False
            })
            raise ValidationError(_("La variación de precio no es correcta."))

        last_transaction = self.get_portal_last_transaction()
        values = {
            "new_amount": new_amount,
            "current_amount": current_amount
        }

        done =  last_transaction.niubiz_confirm_order(values)
        if done:
            self.niubiz_amount = new_amount
        self.niubiz_confirm = last_transaction.niubiz_status_confirm_msg
        self.niubiz_confirm_state = last_transaction.niubiz_status_confirm
        return self.niubiz_confirm_state

    def action_cancel_niubiz(self):
        if not self.is_niubiz:
            raise ValidationError(_("Esta venta no fue procesada con niubiz."))

        if self.niubiz_cancel_state:
            raise ValidationError(_("Esta venta no necesita anulación."))

        if self.niubiz_confirm_state:
            raise ValidationError(_("Esta venta ya fue confirmada, no se puede anular."))
        days = abs((datetime.today() - self.create_date).days)
        if not self.niubiz_countable:
            max_days = 7
        else:
            max_days = 1

        if days > max_days:
            msg = f"Se superó la cantidad maxima ({max_days}) de días para anulias este pedido.{days}"
            self.write({
                'niubiz_confirm_state': msg,
                'niubiz_confirm': False
            })
            raise ValidationError(_(msg))
        last_transaction = self.get_portal_last_transaction()
        last_transaction.niubiz_reverse_order()
        cancel_msg = last_transaction.niubiz_status_cancelled_msg
        if cancel_msg == "Voided":
            cancel_msg = "Cancelada con exito."
        else:
            cancel_msg = "No se pudo cancelar."

        self.niubiz_cancel = cancel_msg
        self.niubiz_cancel_state = last_transaction.niubiz_status_cancelled
        return self.niubiz_cancel_state