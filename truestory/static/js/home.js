function load_articles() {
    // Set an animation while loading.
    var load_btn = $("button#loadMoreReady").detach();
    $("button#loadMoreBusy").removeClass("invisible");

    // Fetch more articles through a GET request to the same page.
    var home_url = window.location.href;
    var cursor_input = $("input#queryCursor");
    $.get({
        url: home_url,
        data: {"queryCursor": cursor_input.val()},
    }).done(function (data) {
        // Get articles row template first.
        var row_tpl = $("div.card-deck").parent().first();
        // Display the newly received articles.
        var bp = data["bias_pairs"];
        for (idx = 0; idx < bp.length; ++idx) {
            var first_data = bp[idx][0], second_data = bp[idx][1];
            // TODO(cmiN): Populate articles with the received data first.
            $("section#articleList").append(row_tpl.clone());
        }

        // Set the next cursor for future retrieval.
        cursor_input.val(data["new_cursor"]);
    }).always(function () {
        // Revert back to the "Load more" button.
        $("button#loadMoreBusy").addClass("invisible");
        $("div#loadGroup").prepend(load_btn);
    });
}


function scroll_top() {
    $(window).scroll(function () {
        if ($(this).scrollTop()) {
            $("#toTop").fadeIn();
        } else {
            $("#toTop").fadeOut();
        }
    });

    $("#toTop").click(function () {
        $("html, body").animate({scrollTop: 0}, 200);
    });
}


to_load.push(scroll_top);
