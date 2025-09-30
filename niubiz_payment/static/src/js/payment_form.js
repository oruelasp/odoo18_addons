/** @odoo-module **/

import paymentForm from '@payment/js/payment_form';

paymentForm.include({
    async _prepareInlineForm(providerId, providerCode, paymentOptionId, paymentMethodCode, flow) {
        // Llamamos primero al comportamiento original
        await this._super(...arguments);

        // Forzamos el flujo 'direct' solo si el proveedor es Niubiz
        if (providerCode === 'niubiz') {
            this._setPaymentFlow('direct');
        }
    }
});