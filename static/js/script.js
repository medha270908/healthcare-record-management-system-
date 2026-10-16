// This project is intentionally kept simple: almost all logic
// happens on the server (Flask) so it is easier to explain in
// a viva. This file only adds a small confirmation before
// re-saving a patient record, so the demo of "modifying" a
// record is a deliberate, visible action.

document.addEventListener("DOMContentLoaded", function () {
    var addForm = document.querySelector('form[action*="add_patient"]');
    if (addForm) {
        addForm.addEventListener("submit", function () {
            console.log("Submitting patient record. A new SHA-256 hash will be generated and sent to the blockchain.");
        });
    }
});
