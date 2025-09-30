/** @odoo-module **/

document.addEventListener("DOMContentLoaded", function () {
    const getInputValue = (name) => {
        return document.querySelector(`#niubiz_data input[name="${name}"]`)?.value || '';
    };

    const data = {
        sessiontoken: getInputValue('session_token'),
        channel: 'web',
        merchantid: getInputValue('merchantId'),
        purchasenumber: getInputValue('order_sequence'),
        amount: parseFloat(getInputValue('amount')).toFixed(2),
        merchantlogo: 'https://i.imgur.com/vXlgTpU.png',
        expirationminutes: 10,
        timeouturl: getInputValue('timeout_url'),
        action: getInputValue('action_url'),
        cancel: () => {
            console.warn("⛔ Usuario canceló el pago.");
        },
    };

    if (typeof VisanetCheckout !== 'undefined') {
        console.log("✅ Ejecutando VisanetCheckout con datos:", data);
        VisanetCheckout.configure(data);
        VisanetCheckout.open();
    } else {
        console.error("❌ VisanetCheckout no está definido.");
    }
});
