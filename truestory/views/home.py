"""Handles the home page."""


from flask import jsonify, render_template, request

from truestory import app


@app.route("/home")
def home():
    """Home page displaying news and available app components."""
    # TODO(cmiN): Extract from DB some biased news pairs.
    bias_pairs = [("a", "b"), ("c", "d"), ("e", "f")]

    cursor = request.args.get("queryCursor")
    if cursor:
        # TODO(cmiN): Use the cursor to fetch the next set of biased articles.
        print(cursor)
        import time; time.sleep(0.5)
        cursor += "_new"
        # Now simulate end of data.
        if cursor.count("new") >= 3:
            cursor = None
        return jsonify({"bias_pairs": bias_pairs, "new_cursor": cursor})

    # TODO(cmiN): Use this keyword when making the cursor's query.
    search = request.args.get("querySearch", "").strip()

    return render_template(
        "home.html",
        title="Search results" if search else None,
        bias_pairs=bias_pairs,
        query_search=search,
        query_cursor="base64_cursor",
    )
