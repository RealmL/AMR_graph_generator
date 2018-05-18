$(document).ready(function () {

    var input = document.getElementById("words");

    input.addEventListener("keyup", function (event) {
        event.preventDefault();
        if (event.keyCode === 13) {
            document.getElementById("query").click();
        }
    });

    $("#query").click(function () {

        $.get('/snts?words=' + $("#words").val(), function (snts, status) {

            $("#myTable tbody tr").remove();

            if (snts.length == 0) {
                alert("未查询到相关结果，请更换查询条件。");
            } else {
                $("#snt_num").val(snts.length);
                snts.forEach(function (item, index) {
                    var tableRef = document.getElementById('myTable').getElementsByTagName('tbody')[0];
                    var newRow = tableRef.insertRow(tableRef.rows.length);
                    newRow.setAttribute("class", "sntclick");
                    newRow.setAttribute("id", item['line_id']);
                    newRow.addEventListener("click", function () {
                        get_data_with_line_id(item['line_id']);
                    });
                    var newCell = newRow.insertCell(0);
                    var t = item['content'];
                    var word_list = $("#words").val().split(" ");
                    word_list.forEach(function (w, index) {
                            if (/\S/.test(w)) {
                                var re = new RegExp(w, "ig");
                                var matchs = t.match(new RegExp(re, 'ig'));
                                if (matchs.length) {
                                    t = t.replace(re, "<span class='myhighlight'><b>" + matchs[0] + "</b></span>");
                                }
                                newCell.innerHTML = t;
                            }
                        }
                    );

                })
            }


        });

    });
});


function get_data_with_line_id(line_id) {
    $.get('/graph?line_id=' + line_id, function (graph, status) {
        draw_with_data(graph);
    });
}

function draw_with_data(graph) {
    var chartDiv = document.getElementById("chart");
    var width = chartDiv.clientWidth;
    var height = chartDiv.clientHeight;

    d3.select("svg").selectAll("*").remove();

    var svg = d3.select("svg");
    svg
        .attr("width", width)
        .attr("height", height);

    svg.append("defs").append("marker")
        .attr("id", "arrowhead")
        .attr("refX", 8 + 3) /*must be smarter way to calculate shift*/
        .attr("refY", 2)
        .attr("markerWidth", 6)
        .attr("markerHeight", 4)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M 0,0 V 4 L6,2 Z"); //this is actual shape for arrowhead

    function color(type) {
        if (type == "normal") {
            return "#2277cd";
        }
        if (type == "literal") {
            return "#72cd13";
        }
        if (type == "root") {
            return "#cd4f59";
        }

    }


    var simulation = d3.forceSimulation()
        .alpha(0.3)
        .force("link", d3.forceLink().distance(70).id(function (d) {
            return d.id;
        }))
        .force("charge", d3.forceManyBody().strength(-3000).distanceMax(160))
        .force('collision', d3.forceCollide().radius(function (d) {
            return 20;
        }))
        .force("center", d3.forceCenter(width / 2, height / 2));

    function dragstarted(d) {
        if (!d3.event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
    }

    function dragended(d) {
        if (!d3.event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    var link = svg.append("g")
        .attr("class", "links")
        .attr("marker-end", "url(#arrowhead)")
        .selectAll("line")
        .data(graph.links)
        .enter().append("line")
        .attr("stroke-width", 4);

    var node = svg.append("g")
        .attr("class", "nodes")
        .selectAll("g")
        .data(graph.nodes)
        .enter().append("g")
        .on("mouseover", handleMouseOver)
        .on("mouseout", handleMouseOut);

    var linktext = svg.append('g')
        .attr("class", "linklabelholder")
        .selectAll("g")
        .data(graph.links)
        .enter().append("g")
        .append("text")
        .attr("class", "linklabel")
        .attr("dx", 1)
        .attr("dy", ".35em")
        .attr("stroke", "#ecbd47")
        .attr("text-anchor", "middle")
        .text(function (d) {
            return d.type
        })
        .on("mouseover", handleMouseOver)
        .on("mouseout", handleMouseOut);

    var circles = node.append("circle")
        .attr("r", 20)
        .attr("fill", function (d) {
            return color(d.type);
        })
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended)
        );


    var node_lables = node.append("text")
        .text(function (d) {
            return d.content;
        })
        .attr('x', 25)
        .attr('y', 5);

    simulation
        .nodes(graph.nodes)
        .on("tick", ticked);


    simulation.force("link")
        .links(graph.links);


    function ticked() {
        link
            .attr("x1", function (d) {
                return d.source.x;
            })
            .attr("y1", function (d) {
                return d.source.y;
            })
            .attr("x2", function (d) {
                return d.target.x;
            })
            .attr("y2", function (d) {
                return d.target.y;
            });

        // link label
        linktext.attr("transform", function (d) {
            return "translate(" + (d.source.x + d.target.x) / 2 + ","
                + (d.source.y + d.target.y) / 2 + ")";
        });

        node
            .attr("transform", function (d) {
                return "translate(" + d.x + "," + d.y + ")";
            })
    }
}

// Create Event Handlers for mouse
function handleMouseOver(d, i) {  // Add interactivity

    // Use D3 to select element, change color and size
    d3.select(this).style(
        "font-size", "300%"
    );

    var circle = d3.select(this).selectAll("circle");
    if (circle) {
        circle.attr('r', 30);
    }
    this.parentElement.appendChild(this);
}

function handleMouseOut(d, i) {
    d3.select(this).style(
        "font-size", "100%"
    );

    var circle = d3.select(this).selectAll("circle");
    if (circle) {
        circle.attr('r', 20);
    }
}
