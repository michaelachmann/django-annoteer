console.log("label_manage_v2.js aktiv!");

document.addEventListener("DOMContentLoaded", function () {
  const addFormBtn = document.getElementById("add-form");
  const formsetContainer = document.getElementById("formset-container");
  const totalForms = document.querySelector("#id_label_set-TOTAL_FORMS");

  if (!addFormBtn || !formsetContainer || !totalForms) return;

  // ➕ Neues Formular hinzufügen
  addFormBtn.addEventListener("click", function () {
    const currentFormCount = parseInt(totalForms.value);
    const newForm = formsetContainer.children[0].cloneNode(true);

    newForm.querySelectorAll("input").forEach(input => {
      if (input.type !== "hidden") input.value = "";
      if (input.name.includes("DELETE")) input.checked = false;
    });

    const regex = new RegExp(`-(\\d+)-`, "g");
    newForm.querySelectorAll("[name], [id], label").forEach((el) => {
      if (el.name) el.name = el.name.replace(regex, `-${currentFormCount}-`);
      if (el.id) el.id = el.id.replace(regex, `-${currentFormCount}-`);
      if (el.tagName.toLowerCase() === "label" && el.htmlFor)
        el.htmlFor = el.htmlFor.replace(regex, `-${currentFormCount}-`);
    });

    const title = newForm.querySelector(".form-label");
    if (title) title.textContent = `Label ${currentFormCount + 1}`;

    formsetContainer.appendChild(newForm);
    totalForms.value = currentFormCount + 1;
  });

  // 🗑 Formular entfernen
  document.addEventListener("click", function (e) {
    if (e.target && e.target.classList.contains("remove-form")) {
      const formDiv = e.target.closest(".formset-form");
      const deleteInput = formDiv.querySelector("input[name$='-DELETE']");

      if (deleteInput) {
        // 📌 Das Formular stammt aus der Datenbank → für Löschung markieren
        deleteInput.value = "on";         // ← 👉 Hier muss es stehen!
        formDiv.style.display = "none";   // Optional: ausblenden
      } else {
        // 📌 Neu hinzugefügtes Formular → einfach entfernen & TOTAL_FORMS verringern
        formDiv.remove();
        const currentTotal = parseInt(totalForms.value);
        totalForms.value = currentTotal - 1;
      }
    }
  });
});