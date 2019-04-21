function select_mini_article(index) {
    // Display selected article.
    if (index) {
        var article_container = $("#relatedArticle" + index);
        var mini_container = $("#relatedMiniArticle" + index);
    } else {
        var article_container = $("#mainArticle");
        var mini_container = $("#mainMiniArticle");
    }
    var place = $("#articlePlace");
    place.empty();
    place.prepend(article_container.find("div.card").clone());

    // Keep the selected one only as not being black & white.
    $("div.articles-scroll").children("div").addClass("black-white");
    mini_container.removeClass("black-white");
}


to_load.push(function () {
    select_mini_article(0);
});
