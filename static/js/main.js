document.querySelectorAll(".filezone").forEach(function (zone) {
  var input = zone.querySelector("input[type=file]");
  var nameEl = zone.querySelector(".filezone-name");
  if (!input) return;
  input.addEventListener("change", function () {
    if (input.files && input.files.length > 0) {
      nameEl.textContent = input.files[0].name;
    } else {
      nameEl.textContent = "";
    }
  });
});

var alertBox = document.getElementById("tb-alert");
if (alertBox) {
  var btn = alertBox.querySelector(".alert-close");
  if (btn) {
    btn.addEventListener("click", function () {
      alertBox.remove();
    });
  }
}