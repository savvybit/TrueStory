var to_load = [];

function loadall() {
    for (idx = 0; idx < to_load.length; ++idx) {
        to_load[idx]();
    }
}

$(loadall);
