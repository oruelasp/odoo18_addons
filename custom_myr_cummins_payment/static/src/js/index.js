/** @odoo-module **/
document.body.style.setProperty("height", "auto", "important");

const btnGuardar = document.getElementById("save_address");
const terminos = document.getElementById("accept_terminos");
const marketing = document.getElementById("accept_marketing");

function actualizarEstadoBoton() {
  btnGuardar.disabled = !(terminos.checked && marketing.checked);
}

function GetZip() {
  const $districtSelect = document.getElementById("l10n_pe_district");
  const $zipInput1 = document.getElementById("o_zip");

  if ($districtSelect && $zipInput1) {
    $districtSelect.addEventListener("change", () => {
      const selectedOption =
        $districtSelect.options[$districtSelect.selectedIndex];
      const zip = selectedOption.getAttribute("data-code");
      console.log(zip);
      if (zip) {
        if ($zipInput1) $zipInput1.value = zip;
        console.log($zipInput1.value);
      }
    });
  }
}
if (window.location.pathname.includes("/shop/address")) {
  GetZip(); // <-- aquí se activa el autollenado del zip
  terminos.addEventListener("change", actualizarEstadoBoton);
  marketing.addEventListener("change", actualizarEstadoBoton);
  actualizarEstadoBoton();
}

// Inicializar al cargar


function initReniecWatcher() {
  const $partner_name = document.getElementById("o_name");
  const $input_vat = document.getElementById("o_vat");
  const $type_ident = document.querySelector("select[name='l10n_latam_identification_type_id']");
  const $company_name = document.getElementById("o_company_name");
  const $company_div = document.getElementById("company_name_div");
  const $direccion = document.getElementById("o_street");
  const $ref_ruc = document.getElementById("ref");
  const $div_country = document.getElementById("div_country");
  const $div_zip = document.getElementById("div_zip");
  const $bloq_data = document.getElementById("bloq_data");
  const $div_identification_type_parent = document.getElementById("div_identification_type_parent");
  const $input_vat_parent = document.getElementById("o_vat_parent");
  const $div_city = document.getElementById("div_city");

  $company_div.style.display = "none";
  $bloq_data.style.display = "none";
  $div_identification_type_parent.style.display = "none";
  $div_country.style.display = "none";
  $div_city.style.display = "none";
  $div_zip.classList.add("o_hidden");
  $div_city.classList.add("o_hidden");

  // Escuchar cambios en tipo de documento
  $type_ident.addEventListener("change", () => {
    const tipo = $type_ident.value;

    if (tipo === "4") {
      $company_div.style.display = "block";
      $bloq_data.style.display = "block";
      $div_identification_type_parent.style.display = "block";
      $partner_name.removeAttribute("readonly");
    } else if (tipo === "5") {
      $company_div.style.display = "none";
      $bloq_data.style.display = "none";
      $div_identification_type_parent.style.display = "none";
      $company_name.value = "";
      $partner_name.setAttribute("readonly", true);
      $company_name.setAttribute("readonly", true);
    } else {
      $company_div.style.display = "none";
      $bloq_data.style.display = "none";
      $div_identification_type_parent.style.display = "none";
      $company_name.value = "";
      $partner_name.removeAttribute("readonly");
      $company_name.setAttribute("readonly", true);
    }

    $partner_name.value = "";
  });

  // Evento para campo de RUC alternativo (campo ref)
  $ref_ruc.addEventListener("keyup", (e) => {
    const numero = e.target.value.trim();

    if (numero.length === 11) {
      fetch("/api/consulta_documento/" + numero)
        .then((res) => res.json())
        .then((data) => {
          if (data.error) return;

          if (data.razonSocial) {
            $partner_name.value = data.razonSocial;
            $direccion.value = data.direccion;
            if (!$input_vat.value) {
              $input_vat.value = numero;
              $type_ident.value = "4";
              $company_div.style.display = "block";
              $partner_name.removeAttribute("readonly");
            }
          }
        })
        .catch((err) => console.error("❌ Error al consultar RUC desde ref:", err));
    }
  });
  if ($input_vat_parent) {
    $input_vat_parent.addEventListener("keyup", (e) => {
      const numero = e.target.value.trim();

      if (numero.length === 8) {
        fetch(`/api/consulta_documento/${numero}`)
          .then((res) => res.json())
          .then((data) => {
            if (!data.error && data.nombreCompleto) {
              const $partner_name = document.getElementById("o_name");
              if ($partner_name) {
                $partner_name.value = data.nombreCompleto;
              }
            }
          })
          .catch((err) => console.error("❌ Error al consultar DNI desde o_vat_parent:", err));
      }
    });
  }

  // Evento principal para o_vat
  $input_vat.addEventListener("keyup", (e) => {
    const numero = e.target.value.trim();
    const tipo = $type_ident.value;

    if (tipo === "5" && numero.length === 8) {
      fetch("/api/consulta_documento/" + numero)
        .then((res) => res.json())
        .then((data) => {
          if (!data.error && data.nombreCompleto) {
            $partner_name.value = data.nombreCompleto;
          }
        })
        .catch((err) => console.error("❌ Error al consultar DNI:", err));
    }

    if (tipo === "4" && numero.length === 11) {
      fetch("/api/consulta_documento/" + numero)
        .then((res) => res.json())
        .then((data) => {
          if (!data.error && data.razonSocial) {
            $company_name.value = data.razonSocial;
            $direccion.value = data.direccion;
          }
        })
        .catch((err) => console.error("❌ Error al consultar RUC:", err));
    }
  });
}


function GetEdithadrees() {
  const $direccion_contacto = document.getElementById("direccion_contacto");
  const $direccion_entrega = document.getElementById("direccion_entrega");

  $direccion_contacto.classList.add("d-none");
  console.log($direccion_contacto);
}

// ✅ Ejecutar solo si estamos en /shop/address
if (window.location.pathname.includes("/shop/address")) {
  initReniecWatcher();
}

const urlParams = new URLSearchParams(window.location.search);
const $status = urlParams.get("status");
if ($status === "edit") {
  GetEdithadrees();
}
