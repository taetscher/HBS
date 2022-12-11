import {loadCSV} from '../load_csv.js';
import {whoAreWe} from '../us.js';
import {formatScore, formatTimestamp} from './format_csv.js';
import {addCheckbox, addCheckbox_ts} from '../add_checkbox.js';

export function visualizeTS(){
    //remove existing visualization and checkboxes
    $("#chart").html("");
    $("#checkboxes").html("");
    $('#sh_button').html('');
    
    
    //build in an option to visualize everything on top of each other (see all games)
    
    //construct an url to the base data
    var ts_baseurl = "https://raw.githubusercontent.com/taetscher/HBS/master/output_csv/gameProgressions/";
    var team = document.getElementById('dropdown_teams').innerHTML;
    var season = document.getElementById('dropdown_seasons').innerHTML;
    var stat = document.getElementById('dropdown_stats').innerHTML;
    stat = stat.replace(/&amp;/g, '&')
    var dataURL = ts_baseurl+team+"/"+season+"/"+stat;
    dataURL = encodeURI(dataURL)
    
    // set up array for chart title
    var date = stat.substr(0,8)
    date = date.split('_').reverse()
    date = date.join('.')
    var title = stat.slice(8,-11).split('_').slice(1);
    var t;
    for (t in title){
        title[t] = title[t].trim()
    }
    
    //load the data
    loadCSV(dataURL).then(function (data){
        //reverse the data so it makes sense
        var data = data.reverse();
        
        //build in mechanism to check if home or away
        var us = whoAreWe();
        var homeAway = 0;
        var check = stat.toLowerCase().split(' ');
        if (us.includes(check[1])){
            homeAway = 1
        }
        
        // format the data
        data.forEach(function(d) {
            d.timestamp = formatTimestamp(d.timestamp)
            d.score = formatScore(d.score, homeAway)
            });
        
        // set the dimensions and margins of the graph
        var margin = {top: 80, right: 50, bottom: 80, left: 60};
        var width = parseInt(d3.select('#viz').style('width'), 10);
        width = width - margin.left - margin.right;
        var height = parseInt(d3.select('#viz').style('height'), 10);
        height = height - margin.top - margin.bottom;

        // set the ranges for svg element
        var x = d3.scaleLinear().range([0, width]);
        var y = d3.scaleLinear().range([height, 0]);
        
        // scale the range of the axes
        x.domain([d3.min(data, function(d){return d.timestamp-0.5}),
                 d3.max(data, function(d){return d.timestamp+0.5})]);
        y.domain([d3.min(data, function(d){return d.score-1}),
                 d3.max(data, function(d){return d.score+1})]);

        // define the area
        var area = d3.area()
            .x(function(d) { return x(d.timestamp); })
            .y0(y(0))
            .y1(function(d) { return y(d.score); });

        // append the svg obgect to the body of the page
        // appends a 'group' element to 'svg'
        // moves the 'group' element to the top left margin
        var svg = d3.select("#chart")
            .attr("preserveAspectRatio", "xMinYMin meet")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");
        
        // gridlines in x axis function
        function make_x_gridlines() {		
            return d3.axisBottom(x)
            .ticks()
            }

        // gridlines in y axis function
        function make_y_gridlines() {
            const yAxisTicks = y.ticks()
                .filter(tick => Number.isInteger(tick));            
            
            return d3.axisLeft(y)
            .tickValues(yAxisTicks)
            }
        
        // add the X gridlines
        svg.append("g")			
          .attr("class", "grid")
          .attr("transform", "translate(0," + height + ")")
          .call(make_x_gridlines()
              .tickSize(-height)
              .tickFormat("")
                )

        // add the Y gridlines
        svg.append("g")			
          .attr("class", "grid")
          .call(make_y_gridlines()
              .tickSize(-width)
              .tickFormat("")
                )

        // add the area
        svg.append("path")
            .data([data])
            .attr("class", "area")
            .attr('stroke', "#ff1c73")
            .attr('fill-opacity', 0.5)
            .attr("d", area);
        
        //add halftime line
        svg.append("g")
            .attr('class', 'halftime')
            .attr("transform", "translate("+ x(30) + ",0)")
            .append("line")
            .attr("y2", height);
        
        //add draw (as in score = 1/-0) line
        svg.append("g")
            .attr('class', 'draw')
            .attr("transform", "translate(0," + y(0) + ")")
            .append("line")
            .attr("x2", width);

        // add the X Axis
        svg.append("g")
            .attr('class', 'axes')
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(x));

        // add the Y Axis
        svg.append("g")
            .attr('class', 'axes')
            .call(make_y_gridlines()
                 .tickFormat(d3.format('.0f')));
        
        // text label for the x axis
        svg.append("text")
            .attr('class', 'axes-label')
            .attr("transform", "translate(" + (width/2) + " ," + (height + margin.top/1.4) + ")")
            .style("text-anchor", "middle")
            .text("Game Time [minutes]");
        
        // text label for the y axis
        svg.append("text")
            .attr('class', 'axes-label')
            .attr("transform", "rotate(-90)")
            .attr("y", 0 - margin.left)
            .attr("x", 0 - (height / 2))
            .attr("dy", "0.8em")
            .style("text-anchor", "middle")
            .text("Goal Differential"); 
        
        // text label for the Title
        svg.append("text")
            .attr('class', 'chart-title')
            .attr("transform", "translate(" + (width/2) + " ," + (0-margin.top/2) + ")")
            .attr("text-anchor", "middle")   
            .text(title[0] + ' vs. ' + title[1] + '  (' + date + ', ' + season.replace('_', '/') +')');
        });
    }


export async function visualizeTS_allGames(in_array){
    //this is a changed copy of visualizeTS()
    //the goal is to add all csv data to the same canvas
    
    //remove existing visualization and checkboxes
    $("#chart").html("");
    $("#checkboxes").html("");
    $("#sh_button").html("");
    
    //set up global function variables
    var len = in_array.length;
    var x_minima = [];
    var x_maxima = [];
    var y_minima = [];
    var y_maxima = [];
    
    //loop over all games' csv files and find min/max values for x and y axes
    var c;
    for (c=0; c<len; c++){
        
        //custom tailor an url to the data
        var ts_baseurl = "https://raw.githubusercontent.com/taetscher/HBS/master/output_csv/gameProgressions/";
        var team = document.getElementById('dropdown_teams').innerHTML;
        var season = document.getElementById('dropdown_seasons').innerHTML;
        var stat = in_array[c];
        stat = stat.replace(/&amp;/g, '&')
        var dataURL = ts_baseurl+team+"/"+season+"/"+stat;
        dataURL = encodeURI(dataURL);
        
        //get the data
        await loadCSV(dataURL).then(function (data){
            
            //reverse the data so it makes sense
            var data = data.reverse();

            //build in mechanism to check if home or away
            var us = whoAreWe();
            var homeAway = 0;
            var check = stat.toLowerCase().split(' ');
            
            if (us.includes(check[1])){
                homeAway = 1
            }
            
            var time = [];
            var score = [];
            // format the data
            data.forEach(function(d) {
                d.timestamp = formatTimestamp(d.timestamp)
                d.score = formatScore(d.score, homeAway)
                time.push(d.timestamp);
                score.push(d.score);
            });

            //append minima and maxima
            x_minima.push(d3.min(time));
            x_maxima.push(d3.max(time));
            y_minima.push(d3.min(score));
            y_maxima.push(d3.max(score));
        });
    }
    
    // set the dimensions and margins of the graph
    var margin = {top: 80, right: 50, bottom: 80, left: 60};
    var width = parseInt(d3.select('#viz').style('width'), 10);
    width = width - margin.left - margin.right;
    var height = parseInt(d3.select('#viz').style('height'), 10);
    height = height - margin.top - margin.bottom;

    // append the svg object to the body of the page
    // appends a 'group' element to 'svg'
    // moves the 'group' element to the top left margin
    var svg = d3.select("#chart")
        .attr("preserveAspectRatio", "xMinYMin meet")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform",
        "translate(" + margin.left + "," + margin.top + ")");
    
    // set the ranges for svg element
    var x = d3.scaleLinear().range([0, width]);
    var y = d3.scaleLinear().range([height, 0]);

    // scale the range of the axes
    x.domain([d3.min(x_minima), d3.max(x_maxima)]);
    y.domain([d3.min(y_minima), d3.max(y_maxima)]);
    
    var q;
    var data_for_all_games = {};
    //LOOP OVER ALL CSVS AND ADD THEM TO CANVAS
    for (q=0; q<len; q++){        
        //construct an url to the base data
        var ts_baseurl = "https://raw.githubusercontent.com/taetscher/HBS/master/output_csv/gameProgressions/";
        var team = document.getElementById('dropdown_teams').innerHTML;
        var season = document.getElementById('dropdown_seasons').innerHTML;
        var stat = in_array[q];
        stat = stat.replace(/&amp;/g, '&')
        var dataURL = ts_baseurl+team+"/"+season+"/"+stat;
        dataURL = encodeURI(dataURL)

        // set up array for chart title
        var date = season;
        var title = 'All Games by '+team+', '+season
        
        //load the data
        await loadCSV(dataURL).then(function (data){
            //reverse the data so it makes sense
            var data = data.reverse();

            //build in mechanism to check if home or away
            var us = whoAreWe();
            var homeAway = 0;
            var check = stat.toLowerCase().split(' ');
            if (us.includes(check[1])){
                homeAway = 1
            }
            
            // format the data
            data.forEach(function(d) {
                d.timestamp = formatTimestamp(d.timestamp)
                d.score = formatScore(d.score, homeAway)
                });
            
            
            // define the area
            var area = d3.area()
                .x(function(d) { return x(d.timestamp); })
                .y0(y(0))
                .y1(function(d) { return y(d.score); });   


            //ONLY ON THE FIRST ONE, ADD AXES, TITLE ETC.
            if (q == 0){

                //console.log(q)
                //console.log(in_array.length-1)

                // add the X gridlines
                svg.append("g")			
                  .attr("class", "grid")
                  .attr("transform", "translate(0," + height + ")")
                  .call(make_x_gridlines()
                      .tickSize(-height)
                      .tickFormat("")
                        )

                // add the Y gridlines
                svg.append("g")			
                  .attr("class", "grid")
                  .call(make_y_gridlines()
                      .tickSize(-width)
                      .tickFormat("")
                        )

                // gridlines in x axis function
                function make_x_gridlines() {		
                    return d3.axisBottom(x)
                    .ticks()
                    }

                // gridlines in y axis function
                function make_y_gridlines() {
                    const yAxisTicks = y.ticks()
                        .filter(tick => Number.isInteger(tick));            

                    return d3.axisLeft(y)
                    .tickValues(yAxisTicks)
                    }

                //add draw (as in score = 1/-0) line
                svg.append("g")
                    .attr('class', 'draw')
                    .attr("transform", "translate(0," + y(0) + ")")
                    .append("line")
                    .attr("x2", width);

                //add halftime line
                svg.append("g")
                    .attr('class', 'halftime')
                    .attr("transform", "translate("+ x(30) + ",0)")
                    .append("line")
                    .attr("y2", height);

                // add the X Axis
                svg.append("g")
                    .attr('class', 'axes')
                    .attr("transform", "translate(0," + height + ")")
                    .call(d3.axisBottom(x));

                // add the Y Axis
                svg.append("g")
                    .attr('class', 'axes')
                    .call(make_y_gridlines()
                         .tickFormat(d3.format('.0f')));

                // text label for the x axis
                svg.append("text")
                    .attr('class', 'axes-label')
                    .attr("transform", "translate(" + (width/2) + " ," + (height + margin.top/1.4) + ")")
                    .style("text-anchor", "middle")
                    .text("Game Time [minutes]");

                // text label for the y axis
                svg.append("text")
                    .attr('class', 'axes-label')
                    .attr("transform", "rotate(-90)")
                    .attr("y", 0 - margin.left)
                    .attr("x", 0 - (height / 2))
                    .attr("dy", "0.8em")
                    .style("text-anchor", "middle")
                    .text("Goal Differential"); 

                // text label for the Title
                svg.append("text")
                    .attr('class', 'chart-title')
                    .attr("transform", "translate(" + (width/2) + " ," + (0-margin.top/2) + ")")
                    .attr("text-anchor", "middle")   
                    .text(title);

                //add a button to show/hide all
                var pDiv = document.getElementById('checkboxes');
                var buttonDiv = document.createElement('div');
                buttonDiv.className = 'd-inline-flex p-2 col-12'
                buttonDiv.id = 'check_all'

                var button = document.createElement('button');
                button.className = "btn btn-primary btn-lg btn-block"
                button.innerHTML = 'Check / Uncheck All'
                button.id = 'checkbox_master';
                button.value = 1;

                buttonDiv.appendChild(button);
                pDiv.appendChild(buttonDiv);


                //prepare functions to manage the button
                function checkAll(){
                    d3.selectAll('.checkbox_box').property('checked', true);
                    d3.selectAll('.area').attr('opacity', 1);
                }
                function uncheckAll(){
                    d3.selectAll('.checkbox_box').property('checked', false);
                    d3.selectAll('.area').attr('opacity', 0);
                }

                //select all paths and checkbox values and set them according to the button
                d3.select('#checkbox_master').on('click', function(){
                    //check if checkboxes are turned on or off
                    var state = d3.select(this).property('value');

                    if (state == 1){
                        //everything is checked, uncheck everything
                        console.log('uncheck');
                        uncheckAll();
                        //set state to 0
                        d3.select(this).property('value', 0);
                    }else{
                        //everything is not checked, check everything
                        console.log('check');
                        checkAll();
                        //set state to 1
                        d3.select(this).property('value', 1);
                    }
                })
            }

            // set up random color
            var color = d3.interpolateInferno(q*1/len);    

            // set up namestring for each game
            var cb_game = stat.replace(' _ ', ' vs ').replace(/ /g,"_").replace('.',"_").replace('-', '_').replace('%', '_').replace('&', '-');
            
            // append checkboxes to div and name them according to game date
            addCheckbox_ts(cb_game, color, q) 

            // add the area
            svg.append("path")
                .data([data])
                .attr("class", "area")
                .attr("stroke", color)
                .attr('stroke-width', '2px')
                .attr('fill-opacity', 0.2)
                .attr('opacity', 1)
                .attr('id', 'line_'+ q)
                .attr("d", area)
                .on('mouseover', function(){
                        d3.select(this)
                            .style('fill-opacity', 1)
                            .style('stroke-width', '4px')
                            .raise();

                        //highlight corresponding checkbox label
                        var lineID = d3.select(this).attr('id');
                        var state = d3.select(this).attr('opacity');

                        if (state == 0){}
                        else{
                            d3.select('#label_'+ cb_game)
                            .style('background-color', '#ff1c73');   
                        }         
                    })
                .on('mouseout', function(){
                        d3.select(this)
                            .style('fill-opacity', 0.2)
                            .style('stroke-width', '2px');

                        var lineID = d3.select(this).attr('id');
                        var state = d3.select(this).attr('opacity');

                        if (state == 0){}
                        else{
                            d3.select('#label_' + cb_game)
                            .style('background-color', null);   
                        }
                    });
            
        });
        
        
        if (q == len-1){
            //on the last pass, add a button to show/hide checkboxes
            var myDiv = document.getElementById('sh_button');
            var sh_b = document.createElement('BUTTON');
            sh_b.innerHTML = '↓↓ advanced selection ↓↓';
            sh_b.setAttribute('class', 'nav-link');
            sh_b.setAttribute('type', 'button');
            sh_b.setAttribute('data-toggle', 'collapse');
            sh_b.setAttribute('data-target', '#checkboxes');
            sh_b.setAttribute('expanded', true);
            sh_b.setAttribute('aria-controls', 'checkboxes');
            sh_b.addEventListener('click', function(){
                //handle innerhtml
                var shown = $('#checkboxes').hasClass('show');
                if (shown){
                    this.innerHTML = '↓↓ advanced selection ↓↓'  
                }else{
                    this.innerHTML = '↑↑ collapse custom selection ↑↑'
                }
            })
            myDiv.appendChild(sh_b)

        }
    }  
    
    // also add a mean/median line to indicate trends at different stages
    // of a game

    var ts_baseurl_m = "https://raw.githubusercontent.com/taetscher/HBS/master/output_csv/gameProgressions/";
    var team_m = document.getElementById('dropdown_teams').innerHTML;
    var season_m = document.getElementById('dropdown_seasons').innerHTML;
    var stat_m = 'median_performance.csv';
    var dataURL_m = ts_baseurl_m+team_m+"/"+season_m+"/"+stat_m;
    var dataURL_median = encodeURI(dataURL_m);
    console.log(dataURL_median)

    //load the data
    await loadCSV(dataURL_median).then(function (data){
        // define the line
        var av_line = d3.line()
            .x(function(d) { return x(d.time); })
            .y(function(d) { return y(d["Median Performance (Whole Season)"]); })
            .curve(d3.curveBasis);

        // add the area behind the line
        svg.append("path")
            .data([data])
            .attr("class", "AverageLine")
            .attr("stroke", "yellow")
            .attr('stroke-width', '35px')
            .attr('stroke-opacity', 0.1)
            .attr('fill-opacity', 0)
            .attr('id', 'average')
            .attr("d", av_line)
        
        // add the line
        svg.append("path")
            .data([data])
            .attr("class", "AverageLine")
            .attr("stroke", "white")
            .attr('stroke-width', '5px')
            .attr('fill-opacity', 0)
            .attr('id', 'average')
            .style("stroke-dasharray", ("3, 3"))
            .attr("d", av_line)
    });
}