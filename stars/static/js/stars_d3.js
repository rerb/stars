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

var r = 200,
    inner_r = .1 * r,
    arc = d3.svg.arc(),
    fill_color = stars_fill()

var get_radius = function(d, i) {
    if(d.data.score != 0)
        return d.data.assessed_points / d.data.available_points * r;
    else
        return inner_r;
}

var credit_title = function(d) {
    return d.data.identifier + ": " + d.data.title + ":\n\n" +
    " Available points: " + d.data.available_points + "\n" +
    " Claimed points: " + d.data.assessed_points;
}

var category_title = function(d) {
    title = d.data.title + ":\n\n" +
    " Score: " + d.data.assessed_points;
    if( d.data.abbreviation != "IN" )
        title += "%";
    return title
}


// Tweens

/* 
    A transition tween that expands from the center
*/
function tweenDonut(b) {
  b.outerRadius = Math.max(inner_r, get_radius(b))
  b.innerRadius = inner_r;
  var i = d3.interpolate({outerRadius: 0, innerRadius: 0, startAngle: b.startAngle, endAngle: b.endAngle}, b);
  return function(t) {
    return arc(i(t));
  };
}

/* 
    A transition tween that expands from the center
    all the way out
*/
function tweenBorder(b) {
  b.outerRadius = r;

  b.innerRadius = inner_r * .5;
  var i = d3.interpolate({outerRadius: 0, innerRadius: 0, startAngle: b.startAngle, endAngle: b.endAngle}, b);
  return function(t) {
    return arc(i(t));
  };
}

/*
    Used to expand and contract the selected category arc
*/
function tweenExpand(b) {
    b.innerRadius = inner_r;
    b.outerRadius = r;
    old_start = b.startAngle;
    old_end = b.endAngle;
    b.startAngle = 0;
    b.endAngle = 2 * Math.PI;
    radius = Math.max(inner_r, get_radius(b))
    var i = d3.interpolate({endAngle: old_end, startAngle: old_start, outerRadius: radius}, b);
    return function(t) {
        return arc(i(t));
      };
}

function tweenExpandBorder(b) {
    b.innerRadius = inner_r * .5;
    b.outerRadius = r;
    old_start = b.startAngle;
    old_end = b.endAngle;
    b.startAngle = 0;
    b.endAngle = 2 * Math.PI;
    var i = d3.interpolate({endAngle: old_end, startAngle: old_start, outerRadius: r}, b);
    return function(t) {
        return arc(i(t));
      };
}

function tweenContract(b) {
  b.innerRadius = inner_r;
  b.outerRadius = Math.max(inner_r, get_radius(b));
  old_start = 0;
  old_end = 2 * Math.PI;
  var i = d3.interpolate({endAngle: old_end, startAngle: old_start, outerRadius: r}, b);
  return function(t) {
      return arc(i(t));
    };
}

function tweenContractBorder(b) {
  b.innerRadius = inner_r * .5;
  b.outerRadius = r;
  old_start = 0;
  old_end = 2 * Math.PI;
  var i = d3.interpolate({endAngle: old_end, startAngle: old_start, outerRadius: r}, b);
  return function(t) {
      return arc(i(t));
    };
}

/*
    Expands and contracts the unselected category arcs
*/
function tweenHide(b) {
  b.innerRadius = 0;
  b.outerRadius = inner_r;
  old_start = b.startAngle;
  old_end = b.endAngle;
  b.startAngle = 0;
  b.endAngle = 2 * Math.PI;
  var i = d3.interpolate({outerRadius: Math.max(inner_r, get_radius(b)), innerRadius: inner_r, startAngle: old_start, endAngle: old_end}, b);
  return function(t) {
      return arc(i(t));
    };
}

function tweenHideBorder(b) {
  b.innerRadius = 0;
  b.outerRadius = inner_r;
  old_start = b.startAngle;
  old_end = b.endAngle;
  b.startAngle = 0;
  b.endAngle = 2 * Math.PI;
  var i = d3.interpolate({outerRadius: r, innerRadius: inner_r * .5, startAngle: old_start, endAngle: old_end}, b);
  return function(t) {
      return arc(i(t));
    };
}

function tweenUnhide(b) {
  b.innerRadius = inner_r;
  b.outerRadius = Math.max(inner_r, get_radius(b));
  var i = d3.interpolate({endAngle: 2 * Math.PI, startAngle: 0, outerRadius: inner_r, innerRadius: 0}, b);
  return function(t) {
      return arc(i(t));
    };
}

function tweenUnhideBorder(b) {
  b.innerRadius = inner_r * .5;
  b.outerRadius = r;
  var i = d3.interpolate({endAngle: 2 * Math.PI, startAngle: 0, outerRadius: inner_r, innerRadius: 0}, b);
  return function(t) {
      return arc(i(t));
    };
}

/*
    Changes to a specified color, or the one based on the index
*/
function tweenColor(c) {
    return function(d, i, a) {
        if(c == null)
            new_color = fill_color(i);
        else
            new_color = c
        return d3.interpolate(a, new_color)
    }
}

/*
    Changes to a opacity
*/
function tweenOpacity(o) {
    return function(d, i, a) {
        return d3.interpolate(a, o)
    }
}