window.addEventListener("beforeprint", function () {
    hideDetails();
});

window.addEventListener("afterprint", function () {
    showDetails();
});

function hideDetails() {
    var detailsElements = document.querySelectorAll("details");
    detailsElements.forEach(function (element) {
        if (!element.open) {
            element.style.display = "none";
        }
    });
}

function showDetails() {
    var detailsElements = document.querySelectorAll("details");
    detailsElements.forEach(function (element) {
        element.style.display = "";
    });
}   