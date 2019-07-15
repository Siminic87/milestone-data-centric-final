// Defering of rendering of graphs until data is loaded
queue()
    .defer(d3.json, "/user_tips/tips")
    .await(makeGraphs);
    
// Function for rendering all graphs
function makeGraphs(error, seoData) {
    var ndx = crossfilter(seoData);

    show_tips_per_category(ndx);
    show_upvotes_per_tip(ndx);
    show_tips_per_date(ndx);

    dc.renderAll();
}

// Tips per Category Chart
function show_tips_per_category(ndx) {
    var dim = ndx.dimension(dc.pluck('category_name'));
    var group = dim.group().reduceCount();

    dc.pieChart("#tips-category")
        .width(310)
        .height(290)
        .radius(100)
        .innerRadius(30)
        .dimension(dim)
        .group(group)
        .colors(d3.scale.category20())
        .legend(dc.legend())
        .renderLabel(true)
        .ordering(function(d) { return -d.key; })
        .label(function(d) { return d.value });
}

// Upvotes per Tip Chart
function show_upvotes_per_tip(ndx) {
    var dim = ndx.dimension(dc.pluck('tip_name'));
    var group = dim.group().reduceSum(dc.pluck('upvotes'));

    dc.barChart("#upvotes-tip")
        .width(330)
        .height(290)
        .margins({ top: 10, right: 55, bottom: 30, left: 25 })
        .dimension(dim)
        .group(group)
        .transitionDuration(500)
        .x(d3.scale.ordinal())
        .xUnits(dc.units.ordinal)
        .yAxis().ticks(20);
}

// Tips per Date Chart
function show_tips_per_date(ndx) {
    var dim = ndx.dimension(dc.pluck('date'));
    var group = dim.group().reduceCount();

    dc.barChart("#tips-date")
        .width(330)
        .height(290)
        .margins({ top: 10, right: 55, bottom: 30, left: 25 })
        .dimension(dim)
        .group(group)
        .transitionDuration(500)
        .x(d3.scale.ordinal())
        .xUnits(dc.units.ordinal)
        .yAxis().ticks(20);
}