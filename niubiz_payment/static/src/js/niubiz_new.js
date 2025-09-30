// if (typeof document !== 'undefined') {
//     const getInputValue = function (name) {
//         const inputElement = document.querySelector(`#niubiz_data input[name="${name}"]`);
//         return inputElement ? inputElement.value : null;
//     }

//     document.addEventListener('DOMContentLoaded', function () {
//         const payButton = document.querySelector('[name="o_payment_submit_button"]');

//         if (!payButton) {
//             console.warn('No se encontró el botón de pago.');
//             return;
//         }

//         payButton.addEventListener('click', function (e) {
//             e.preventDefault(); // Evita el envío del formulario

//             const blockUI = document.createElement('div');
//             blockUI.innerHTML = '<h2 class="text-white"><img src="/web/static/img/spin.svg" class="fa-pulse"/>' +
//                 '    <br /> </h2>';
//             blockUI.style.position = 'fixed';
//             blockUI.style.top = '0';
//             blockUI.style.left = '0';
//             blockUI.style.width = '100%';
//             blockUI.style.height = '100%';
//             blockUI.style.backgroundColor = 'rgba(0,0,0,0.5)';
//             blockUI.style.zIndex = '9999';
//             blockUI.style.display = 'flex';
//             blockUI.style.justifyContent = 'center';
//             blockUI.style.alignItems = 'center';
//             document.body.appendChild(blockUI);

//             const scriptNiubiz = document.createElement('script');
//             scriptNiubiz.src = getInputValue('checkout_form');
//             scriptNiubiz.async = true;
//             scriptNiubiz.defer = true;
//             scriptNiubiz.onload = function () {
//                 const data = {
//                     sessiontoken: getInputValue('session_token'),
//                     channel: 'web',
//                     merchantid: getInputValue('merchant_id'),
//                     purchasenumber: getInputValue('order_sequence'),
//                     amount: parseFloat(getInputValue('amount')).toFixed(2),
//                     merchantlogo: 'https://i.imgur.com/vXlgTpU.png',
//                     expirationminutes: '10',
//                     timeouturl: getInputValue('timeout_url'),
//                     action: getInputValue('action_url'),
//                     cancel: function () {
//                         console.log('Cancelación del pago.');
//                         const loader = document.querySelector('#o_payment_form_pay .o_loader');
//                         if (loader) loader.remove();
//                         const payButton = document.querySelector('#o_payment_form_pay');
//                         if (payButton) payButton.disabled = false;
//                         document.body.removeChild(blockUI);
//                     }
//                 };

//                 console.log('Configurando VisanetCheckout con los siguientes datos:', data);
//                 VisanetCheckout.configure(data);
//                 VisanetCheckout.open();

//                 setTimeout(function () {
//                     const isNiubiz = document.querySelector("#visaNetJS")?.offsetParent !== null;
//                     console.log('¿Está visible Niubiz?', isNiubiz);
//                     if (isNiubiz) {
//                         document.body.removeChild(blockUI);
//                     }
//                 }, 3000);
//             };

//             const niubizData = document.getElementById('niubiz_data');
//             niubizData.appendChild(scriptNiubiz);
//         });
//     });
// }
