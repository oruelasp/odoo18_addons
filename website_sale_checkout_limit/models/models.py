# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request
from datetime import datetime
from odoo.tools import float_round
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    no_send_sap = fields.Boolean(string="No enviar a SAP")
    alert_gesintel = fields.Boolean(
        string="Alerta Gesintel", default=False, help="Indica si hay alerta de Gesintel"
    )
    message_gesintel = fields.Text(
        string="Mensaje Gesintel", help="Mensaje desde Gesintel sobre esta orden"
    )


class Website(models.Model):
    _inherit = "website"

    def _convert_to_usd(self, currency, amount, company, date):
        usd = self.env.ref("base.USD")
        return (
            amount
            if currency.name == "USD"
            else currency._convert(amount, usd, company, date)
        )

    def check_cart_amount(self):
        # Obtener la orden actual del carrito
        order = request.website.sale_get_order()
        if not order:
            _logger.info("[CHECK_CART] No hay orden de carrito activa.")
            return True

        ircsudo = self.env["ir.config_parameter"].sudo()
        min_checkout_amount = ircsudo.get_param(
            "website_sale_checkout_limit.min_checkout_amount"
        )
        min_amount_type = ircsudo.get_param(
            "website_sale_checkout_limit.min_amount_type"
        )

        vat = order.partner_id.vat if order.partner_id else ""
        if not vat:
            _logger.info(f"[CHECK_CART] El cliente no tiene RUC/DNI asignado.")
            return True
        _logger.info(f"[CHECK_CART] VAT {vat}.")

        current_year = datetime.today().year
        domain = [
            "&",
            "&",
            "&",
            ("partner_id.vat", "=", vat),
            ("state", "in", ["sale"]),
            ("date_order", ">=", f"{current_year}-01-01"),
            ("date_order", "<=", f"{current_year}-12-31"),
        ]

        previous_orders = self.env["sale.order"].sudo().search(domain)
        _logger.info(f"[CHECK_CART] DOMAIN: {domain}")
        _logger.info(f"[CHECK_CART] COTIZACIONES: {previous_orders}")

        total_previous = 0.0

        for prev in previous_orders:
            converted = self._convert_to_usd(
                prev.currency_id, prev.amount_total, prev.company_id, prev.date_order
            )
            total_previous += converted

        total_previous = float_round(total_previous, precision_digits=2)

        _logger.info(f"[CHECK_CART] Total ventas anteriores (USD): {total_previous}")
        _logger.info(f"[CHECK_CART] Límite mínimo de compra: {min_checkout_amount}")
        _logger.info(f"[CHECK_CART] Tipo de monto a evaluar: {min_amount_type}")

        # Monto de la orden actual (en USD)
        today = order.date_order or fields.Date.today()
        if min_amount_type == "untaxed":
            current_amount = self._convert_to_usd(
                order.currency_id, order.amount_untaxed, order.company_id, today
            )
        else:
            current_amount = self._convert_to_usd(
                order.currency_id, order.amount_total, order.company_id, today
            )

        current_amount = float_round(current_amount, precision_digits=2)
        total_combined = current_amount + total_previous

        _logger.info(f"[CHECK_CART] Monto actual del carrito (USD): {current_amount}")
        _logger.info(
            f"[CHECK_CART] Total combinado (actual + previas): {total_combined}"
        )

        limit = float(min_checkout_amount)

        if total_combined > limit:
            order.write({"no_send_sap": True})
            _logger.info(f"[CHECK_CART] Límite excedido. no_send_sap = True.")
            return False
        else:
            order.write({"no_send_sap": False})
            _logger.info(f"[CHECK_CART] Límite NO excedido. no_send_sap = False.")
            return True

    def info_message(self):
        ircsudo = self.env["ir.config_parameter"].sudo()
        return ircsudo.get_param("website_sale_checkout_limit.info_message")


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    min_checkout_amount = fields.Float(string="Minimum Amount to Checkout")
    min_amount_type = fields.Selection(
        [("untaxed", "Tax Excluded"), ("taxed", "Tax Included")], string="Tipo de Monto"
    )
    info_message = fields.Text(
        string="Mensaje informativo para el cliente",
        translate=True,
        default="¡Gracias por tu interés en nuestros productos! Hemos recibido tus datos y un agente se pondrá en contacto contigo pronto.",
    )

    def set_values(self):
        super().set_values()
        self.env["ir.config_parameter"].set_param(
            "website_sale_checkout_limit.min_checkout_amount", self.min_checkout_amount
        )
        self.env["ir.config_parameter"].set_param(
            "website_sale_checkout_limit.min_amount_type", self.min_amount_type
        )
        self.env["ir.config_parameter"].set_param(
            "website_sale_checkout_limit.info_message", self.info_message
        )

    @api.model
    def get_values(self):
        res = super().get_values()
        ircsudo = self.env["ir.config_parameter"].sudo()
        res.update(
            min_checkout_amount=float(
                ircsudo.get_param("website_sale_checkout_limit.min_checkout_amount")
                or 1000
            ),
            min_amount_type=ircsudo.get_param(
                "website_sale_checkout_limit.min_amount_type"
            )
            or "untaxed",
            info_message=ircsudo.get_param("website_sale_checkout_limit.info_message")
            or self.info_message.default,
        )
        return res
