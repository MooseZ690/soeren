window.addEventListener("beforeunload", () => {
    sessionStorage.setItem("scrollY", window.scrollY);
});

window.addEventListener("load", () => {
    const scrollY = sessionStorage.getItem("scrollY");
    if (scrollY !== null) {
        window.scrollTo(0, parseInt(scrollY, 10));
    }
});