var to_load = [];


function loadall() {
    for (idx = 0; idx < to_load.length; ++idx) {
        to_load[idx]();
    }
}


function nav_set_active() {
    // Deactivate any active tab.
    $("#appNav .nav-item.active").removeClass("active");
    // Set focus on the one corresponding to the current URL.
    var url_path = window.location.pathname;
    var active_tab = $('a.nav-link[href="' + url_path + '"]').parent();
    active_tab.addClass("active");
    // Don't forget about the screen-reader helper.
    active_tab.find("span.sr-only").text("(current)");
}


to_load.push(nav_set_active);

$(loadall);
