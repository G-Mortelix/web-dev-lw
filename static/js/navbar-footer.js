// JavaScript for ensuring sticky navbar and footer with smooth scrolling
document.addEventListener("DOMContentLoaded", function() {
    // Ensure content doesn't overflow in a way that hides scrolling
    document.body.style.overflowX = "hidden"; // Prevent horizontal overflow
    window.addEventListener("resize", adjustForZoomAndScroll);

    function adjustForZoomAndScroll() {
        // Calculate body height to account for zooming behavior
        const body = document.body;
        const html = document.documentElement;
        const contentHeight = Math.max(
            body.scrollHeight, body.offsetHeight, 
            html.clientHeight, html.scrollHeight, html.offsetHeight
        );

        if (contentHeight > window.innerHeight) {
            document.body.style.overflowY = "auto"; // Allow vertical scrolling
        } else {
            document.body.style.overflowY = "hidden"; // Hide vertical overflow when unnecessary
        }
    }

    adjustForZoomAndScroll();
});
