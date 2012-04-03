/*
    Contains some commonly used tools for working
    with d3.js
*/

var stars_fill_colors = [    
    "#d8d8be", "#d8d0c5", "#dbdad8", "#e2dbcb",
    "#bfc094", "#c2b2a3", "#c6c2c1", "#cfc3a9"
]
    // "#a9ad70", "#aa9882", "#b1adac", "#bfb18e",
var stars_stroke_colors = [
    "#939a4c", "#99836b", "#9d9998", "#af9e73",
    "#858f38", "#8c7458", "#908c89", "#a39161"
];

stars_fill = function() {
    return d3.scale.ordinal().range(stars_fill_colors);
};

stars_stroke = function() {
    return d3.scale.ordinal().range(stars_stroke_colors);
};

function tweenOpacity(o) {
return function(d, i, a) {
    return d3.interpolate(a, o)
}
}