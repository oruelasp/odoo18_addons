/** @odoo-module **/

console.log("✅ INICIO DEL NIUBIZ");

const payButton = document.querySelector('[name="o_payment_submit_button"]');
if (!payButton) return;

payButton.addEventListener("click", function (e) {
    e.preventDefault();

    const form = document.querySelector("#o_payment_form");
    const txRoute = form?.getAttribute('data-transaction-route');
    const txId = txRoute?.split("/").pop();

    if (!txId) {
        alert("❌ No se pudo obtener el ID de la transacción.");
        return;
    }

    // ⏱ Esperamos que termine el procesamiento del backend
    setTimeout(async () => {
        try {
            const response = await fetch(`/payment/niubiz/sdk_data/${txId}`);
            const data = await response.json();
            console.log(data)
            if (!response.ok || data.error) {
                alert("❌ Error al obtener datos: " + (data.error || response.statusText));
                return;
            }

            // Cargamos el SDK
            const script = document.createElement("script");
            script.src = data.checkout_form;
            script.onload = () => {
                if (typeof VisanetCheckout === "undefined") {
                    alert("❌ El SDK de Niubiz no se cargó correctamente.");
                    return;
                }

                VisanetCheckout.configure({
                    sessiontoken: data.sessiontoken,
                    channel: "web",
                    merchantid: data.merchantid,
                    purchasenumber: data.purchasenumber,
                    amount: parseFloat(data.amount).toFixed(2),
                    merchantlogo: "https://www.interperu.pe/uploads/repuestos/marcas/cummins-marcas-apuestan-interperu-camiones.png",
                    expirationminutes: 20,
                    timeouturl: data.timeouturl,
                    action: data.action,
                    cancel: () => {
                        console.log("❌ Cancelado por el usuario");
                        window.location.reload()
                    },
                    paymentmethods: ["card"],
                });

                VisanetCheckout.open();
            };

            document.body.appendChild(script);
        } catch (err) {
            console.error("⚠️ Error al comunicarse con el backend:", err);
            alert("Hubo un problema al iniciar el pago con Niubiz.");
        }
    }, 2000); // ⏳ Espera de 1.2 segundos para garantizar consistencia
});