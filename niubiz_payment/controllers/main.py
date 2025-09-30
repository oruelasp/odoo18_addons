from odoo import http, fields, _
from odoo.http import request, route
from odoo.exceptions import AccessError, MissingError
from odoo.addons.sale.controllers.portal import CustomerPortal
from odoo.addons.website_sale.controllers.main import WebsiteSale
import json
import logging
import werkzeug.utils
_logger = logging.getLogger(__name__)


class NiubizController(http.Controller):

    @http.route(
        "/payment/niubiz/sdk_data/<int:tx_id>",
        type="http",
        auth="public",
        csrf=False,
        website=True,
    )
    def niubiz_sdk_data(self, tx_id, **kwargs):
        order = request.website.sale_get_order()
        tx = (
            request.env["payment.transaction"]
            .sudo()
            .search([("sale_order_ids", "in", order.id)], limit=1, order="id desc")
        )

        reference = tx.reference
        if not tx or not tx.exists():
            return request.make_response(
                json.dumps({"error": "Transacción no encontrada"}),
                headers=[("Content-Type", "application/json")],
            )

        # ✅ Usamos los valores ya almacenados
        if not tx.niubiz_session_token:
            return request.make_response(
                json.dumps({"error": "Faltan datos del token Niubiz"}),
                headers=[("Content-Type", "application/json")],
            )

        data = {
            "sessiontoken": tx.niubiz_session_token,
            "merchantid": tx.niubiz_merchant_id,
            "purchasenumber": tx.niubiz_order_sequence,
            "amount": tx.niubiz_amount,
            "timeouturl": tx.niubiz_timeout_url,
            "action": tx.niubiz_action_url,
            "checkout_form": tx.niubiz_checkout_form,
        }

        return request.make_response(
            json.dumps(data), headers=[("Content-Type", "application/json")]
        )

    @http.route(
        ["/payment/niubiz/capture/<string:tx>/<string:purchase_number>"],
        type="http",
        auth="public",
        csrf=False,
    )
    def payment_capture(self, tx, purchase_number, **kwargs):
        payment_token = kwargs.get("transactionToken")
        if not payment_token:
            _logger.warning("⚠️ No se recibió transactionToken.")
            return werkzeug.utils.redirect("/payment/status?state=error")

        reference = tx.replace("_", "/")
        kwargs["reference"] = reference
        kwargs["purchase_number"] = purchase_number

        capture_response = (
            request.env["payment.transaction"].sudo()._create_niubiz_capture(kwargs)
        )

        tx_obj = (
            request.env["payment.transaction"]
            .sudo()
            .search([("reference", "=", reference)], limit=1)
        )
        if not tx_obj:
            _logger.error(f"❌ No se encontró transacción con referencia {reference}")
            return werkzeug.utils.redirect("/payment/status?state=error")

        # Guardar referencia del proveedor
        tx_obj.write({"provider_reference": capture_response.get("reference")})

        # Manejo del estado del pago
        status = capture_response.get("status")
        if status == "authorized":
            sale_order = tx_obj.sale_order_ids and tx_obj.sale_order_ids[0]
            tx_obj._set_done()  # Marca la transacción como exitosa
            confirm_template = request.env.ref(
                "niubiz_payment.email_confirm_sale_order", raise_if_not_found=False
            )
            pago_template = request.env.ref(
                "niubiz_payment.email_pago_confirm_sale", raise_if_not_found=False
            )

            # ✅ Confirmar orden y enviar correo
            if sale_order and sale_order.state in ["draft", "sent"]:

                sale_order.action_confirm()

            # Redirigir al usuario a la página de confirmación
            return werkzeug.utils.redirect(f"/my/orders/{sale_order.id}")

        elif status == "denied":
            tx_obj._set_error("Error al procesar el pago.")

            return werkzeug.utils.redirect("/payment/status?state=error")
        else:
            tx_obj._set_canceled()
            return werkzeug.utils.redirect("/payment/status?state=cancel")

    @http.route(["/payment/niubiz/timeout"], type="http", auth="public", csrf=False)
    def payment_timeout(self, **kwargs):
        return "<pre>⚠️ El tiempo de espera para el pago ha finalizado. Inténtalo nuevamente.</pre>"

    @http.route(["/payment/niubiz/error"], type="http", auth="public", csrf=False)
    def payment_error_niubiz(self, **kwargs):
        return """
            <div style="text-align:center;">
                <h1 style="color:red;">❌ Error al procesar el pago con Niubiz</h1>
                <p>Por favor, verifica tu conexión o vuelve a intentarlo más tarde.</p>
            </div>
        """


class CustomerPortalCustom(CustomerPortal):

    @http.route(["/my/orders/<int:order_id>"], type="http", auth="public", website=True)
    def portal_order_page(
        self,
        order_id,
        report_type=None,
        access_token=None,
        message=False,
        download=False,
        downpayment=None,
        **kw,
    ):
        try:
            order_sudo = self._document_check_access(
                "sale.order", order_id, access_token=access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

        if report_type in ("html", "pdf", "text"):
            # CAMBIAR A TU REPORTE PERSONALIZADO
            return self._show_report(
                model=order_sudo,
                report_type=report_type,
                report_ref="niubiz_payment.action_reporte_sale_order",  # ← aquí pones el nuevo XML ID del reporte
                download=download,
            )

        # LOG DE VISTO POR CLIENTE (puedes dejarlo igual si no quieres cambiarlo)
        if request.env.user.share and access_token:
            today = fields.Date.today().isoformat()
            session_obj_date = request.session.get(f"view_quote_{order_sudo.id}")
            if session_obj_date != today:
                request.session[f"view_quote_{order_sudo.id}"] = today
                author = (
                    order_sudo.partner_id
                    if request.env.user._is_public()
                    else request.env.user.partner_id
                )
                msg = _("Cotización vista por el cliente %s", author.name)

                # MODIFICACIÓN AQUÍ: NUEVO SUBTIPO EN EL CHATTER
                order_sudo.message_post(
                    author_id=author.id,
                    body=msg,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",  # ← cambia aquí si tienes un subtipo personalizado
                )

        backend_url = (
            f"/odoo/action-{order_sudo._get_portal_return_action().id}/{order_sudo.id}"
        )
        values = {
            "sale_order": order_sudo,
            "product_documents": order_sudo._get_product_documents(),
            "message": message,
            "report_type": "html",
            "backend_url": backend_url,
            "res_company": order_sudo.company_id,
        }

        if order_sudo._has_to_be_paid():
            values.update(
                self._get_payment_values(
                    order_sudo,
                    downpayment=(
                        downpayment == "true"
                        if downpayment is not None
                        else order_sudo.prepayment_percent < 1.0
                    ),
                )
            )

        history_session_key = (
            "my_quotations_history"
            if order_sudo.state in ("draft", "sent", "cancel")
            else "my_orders_history"
        )

        values = self._get_page_view_values(
            order_sudo, access_token, values, history_session_key, False
        )
        return request.render("sale.sale_order_portal_template", values)


class WebsiteSaleDeliveryCustom(WebsiteSale):

    def _order_summary_values(self, order, **kwargs):
        """
        Custom summary values:
        - amount_delivery: sin IGV
        - amount_untaxed: solo productos
        - amount_tax: solo productos
        - amount_total: como está (Odoo ya lo calcula bien)
        """
        Monetary = request.env["ir.qweb.field.monetary"]
        currency = order.currency_id

        # Separar líneas
        delivery_lines = order.order_line.filtered(lambda l: l.is_delivery)
        product_lines = order.order_line.filtered(lambda l: not l.is_delivery)

        # Calcular montos
        delivery_untaxed = sum(delivery_lines.mapped("price_subtotal"))
        product_untaxed = sum(product_lines.mapped("price_subtotal"))
        product_tax = sum(product_lines.mapped("price_tax"))

        return {
            "success": True,
            "is_free_delivery": delivery_untaxed == 0.0,
            "amount_delivery": Monetary.value_to_html(
                delivery_untaxed, {"display_currency": currency}
            ),
            "amount_untaxed": Monetary.value_to_html(
                product_untaxed, {"display_currency": currency}
            ),
            "amount_tax": Monetary.value_to_html(
                order.amount_tax, {"display_currency": currency}
            ),
            "amount_total": Monetary.value_to_html(
                order.amount_total, {"display_currency": currency}
            ),
        }

    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True, sitemap=False)
    def shop_confirm_order(self, **post):
        is_min = request.website.check_cart_amount()
        if is_min:
            _logger.info("Cart amount is sufficient, proceeding to checkout")
            return super(WebsiteSaleDeliveryCustom, self).shop_confirm_order(**post)
        return request.redirect("/confirmacion-control-de-compras-anuales")