function smooth_navigation() {
    // Smooth scrolling using jQuery easing.
    $('a.js-scroll-trigger[href*="#"]:not([href="#"])').click(function () {
        if (location.pathname.replace(/^\//, "") == this.pathname.replace(/^\//, "") &&
                location.hostname == this.hostname) {
            var target = $(this.hash);
            target = target.length ? target : $("[name=" + this.hash.slice(1) + "]");
            if (target.length) {
                $("html, body").animate({
                    scrollTop: (target.offset().top - 70)
                }, 1000, "easeInOutExpo");
                return false;
            }
        }
    });

    // Closes responsive menu when a scroll trigger link is clicked.
    $(".js-scroll-trigger").click(function () {
        $(".navbar-collapse").collapse("hide");
    });

    // Activate scrollspy to add active class to navbar items on scroll.
    $("body").scrollspy({
        target: "#mainNav",
        offset: 100
    });

    // Collapse Navbar.
    var navbarCollapse = function () {
        if ($("#mainNav").offset().top > 100) {
          $("#mainNav").addClass("navbar-shrink");
        } else {
          $("#mainNav").removeClass("navbar-shrink");
        }
    };
    // Collapse now if page is not at top.
    navbarCollapse();
    // Collapse the navbar when page is scrolled.
    $(window).scroll(navbarCollapse);
}


function captcha_form(event) {
    // Displays the captcha for e-mail submit.
    event.preventDefault();
    $("form#saveMail").find("input, button").addClass("d-none");
    $("div#antiRobot").removeClass("d-none");
    return false;
}


function captcha_submit(captcha_response) {
    // Submits mail and displays storing status.
    var form = $("form#saveMail");
    $.post({
        url: window.location.origin + form.attr("action"),
        data: {
            captchaResponse: captcha_response,
            mail: form.find("input#mail").val()
        }
    }).done(function (recv_data) {
        if (recv_data["status"]) {
            $("div#successText").removeClass("d-none");
        } else {
            $("div#duplicateText").removeClass("d-none");
        }
    }).fail(function (recv_data) {
        $("div#failText").removeClass("d-none");
    }).always(function () {
        $("div#antiRobot").addClass("d-none");
    });
}


function improveAppearance() {
    $("a#typeformSurvey").addClass("typeform-share-big");
}


to_load.push(smooth_navigation, improveAppearance);
