function select_mini_article(index) {
    if (index) {
        var article_container = $("#relatedArticle" + index);
    } else {
        var article_container = $("#mainArticle");
    }

    var place = $("#articlePlace");
    place.empty();
    place.prepend(article_container.find("div.card").clone());
}


to_load.push(function () {
    select_mini_article(0);
})
