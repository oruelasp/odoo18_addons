/** @odoo-module **/

document.addEventListener("DOMContentLoaded", function () {
  // ========================
  // Cargar tipos de documento
  // ========================
  fetch("/document/types", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  })
    .then((res) => res.json())
    .then((data) => {
      const select = document.getElementById("identification_type_select");
      const selectedId = parseInt(select.getAttribute("data-selected-id")); // obtener valor inicial
      if (select) {
        data.forEach((item) => {
          const option = document.createElement("option");
          option.value = item.id;
          option.textContent = item.name;
          if (item.id === selectedId) {
            option.setAttribute("selected", "True");
          }
          select.appendChild(option);
        });

        // ✅ Solo marcar como obligatorio cuando ya está cargado
        select.setAttribute("required", "required");
      }
    });

  // ========================
  // Cargar provincias según departamento
  // ========================
  const stateSelect = document.querySelector('select[name="state_id"]');
  const citySelect = document.querySelector('select[name="city_id"]');

  if (stateSelect && citySelect) {
    stateSelect.addEventListener("change", function () {
      const stateId = this.value;
      citySelect.innerHTML = '<option value="">Seleccione...</option>';
      if (!stateId) return;

      fetch("/get/provincias", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ state_id: stateId }),
      })
        .then((res) => res.json())
        .then((cities) => {
          cities.forEach((city) => {
            const opt = document.createElement("option");
            opt.value = city.id;
            opt.textContent = city.name;
            citySelect.appendChild(opt);
          });
        });
    });
  }

  // ========================
  // Cargar distritos según provincia
  // ========================
  const districtSelect = document.querySelector(
    'select[name="l10n_pe_district"]'
  );

  if (citySelect && districtSelect) {
    citySelect.addEventListener("change", function () {
      const cityId = this.value;
      districtSelect.innerHTML = '<option value="">Seleccione...</option>';
      if (!cityId) return;

      fetch("/get/distritos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ city_id: cityId }),
      })
        .then((res) => res.json())
        .then((districts) => {
          districts.forEach((d) => {
            const opt = document.createElement("option");
            opt.value = d.id;
            opt.textContent = d.name;
            opt.setAttribute("zip", d.code || "");
            districtSelect.appendChild(opt);
          });
        });
    });
  }

  // ========================
  // Actualizar ZIP al cambiar distrito
  // ========================
  const zipInput = document.querySelector('input[name="zipcode"]');
  if (districtSelect && zipInput) {
    districtSelect.addEventListener("change", function () {
      const selected = this.options[this.selectedIndex];
      const zip = selected.getAttribute("zip") || "";
      zipInput.value = zip;
    });
  }
});

/** @odoo-module **/

document.body.style.setProperty("height", "auto", "important");

function initReniecWatcher() {
  const $partner_name = document.querySelector("input[name='name']");
  const $input_vat = document.querySelector("input[name='vat']");
  const $type_ident = document.querySelector(
    "select[name='l10n_latam_identification_type_id']"
  );
  const $company_name = document.querySelector("input[name='company_name']");
  const $direccion = document.querySelector("input[name='street']");
  const $company_div = document
    .querySelector("input[name='company_name']")
    ?.closest("div");

  if (!$input_vat || !$type_ident) return;

  if ($company_div) $company_div.classList.add("d-none");

  $type_ident.addEventListener("change", () => {
    const tipo = $type_ident.value;
    if (tipo === "4") {
      // RUC
      if ($company_div) $company_div.classList.remove("d-none");
      $partner_name.removeAttribute("readonly");
    } else if (tipo === "5") {
      // DNI
      if ($company_div) $company_div.classList.add("d-none");
      $company_name.value = "";
      $partner_name.setAttribute("readonly", true);
    } else {
      if ($company_div) $company_div.classList.add("d-none");
      $company_name.value = "";
      $partner_name.removeAttribute("readonly");
    }
    $partner_name.value = "";
  });

  $input_vat.addEventListener("keyup", (e) => {
    const numero = e.target.value.trim();
    const tipo = $type_ident.value;

    if (tipo === "5" && numero.length === 8) {
      // DNI - RENIEC
      fetch(`/api/consulta_documento/${numero}`)
        .then((res) => res.json())
        .then((data) => {
          if (!data.error && data.nombreCompleto) {
            $partner_name.value = data.nombreCompleto;
            $company_name.value = "";
          }
        })
        .catch((err) => console.error("❌ Error consultando RENIEC:", err));
    }

    if (tipo === "4" && numero.length === 11) {
      // RUC - SUNAT
      fetch(`/api/consulta_documento/${numero}`)
        .then((res) => res.json())
        .then((data) => {
          if (!data.error && data.razonSocial) {
            $company_name.value = data.razonSocial;
            $direccion.value = data.direccion;
            $partner_name.value = "";
            if ($company_div) $company_div.classList.remove("d-none");
            $partner_name.removeAttribute("readonly");
          }
        })
        .catch((err) => console.error("❌ Error consultando SUNAT:", err));
    }
  });
}

initReniecWatcher();
