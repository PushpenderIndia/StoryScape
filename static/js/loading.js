document.addEventListener("DOMContentLoaded", function () {
    const loader = document.getElementById("loader");

    function simulateLoading() {
        let width = 0;
        const intervalId = setInterval(function () {
            width += 10;
            loader.style.width = width + "%";

            if (width >= 100) {
                clearInterval(intervalId);
                console.log("Loading complete!");
            }
        }, 200);
    }

    simulateLoading();
});
