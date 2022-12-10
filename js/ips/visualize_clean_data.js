import {addCheckbox} from '../../js/add_checkbox.js'

export function vizClean(data){
    
    console.log('clean')
    //console.log(data)
    
    //set up title
    var team = document.getElementById('dropdown_teams').innerHTML;
    var season = document.getElementById('dropdown_seasons').innerHTML;
    var stat = document.getElementById('dropdown_stats').innerHTML;
    stat = stat.replace(/&amp;/g, '&')
    var title = stat + " (" + team + ", " + season.replace('_', '/') + ")";

    
    // set the dimensions and margins of the graph
    var margin = {top: 80, right: 50, bottom: 120, left: 60};
    var width = parseInt(d3.select('#viz').style('width'), 10);
    width = width - margin.left - margin.right;
    var height = parseInt(d3.select('#viz').style('height'), 10);
    height = height - margin.top - margin.bottom;
    
    // append the svg obgect to the body of the page
    // appends a 'group' element to 'svg'
    // moves the 'group' element to the top left margin
    var svg = d3.select('#chart')
            .attr("preserveAspectRatio", "xMinYMin meet")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");
    
    //loop through the data a first time to get ranges for y axis
    var stat_minima = [];
    var stat_maxima = [];
    var q;
    for (n=0; n < data.length; n++ ){
        //convert the data
        var player = data[n].SPIELER || data[n].KADER || data[n].TORHÜTER || data[n]['TORHÜTER*IN'];
        
        //convert statistics to numbers
        var statistics_r = Object.values(data[n]);
        statistics_r.shift()
        for (e in statistics_r){
            statistics_r[e] = Number(statistics_r[e])
        }
        
        stat_minima.push(d3.min(statistics_r))
        stat_maxima.push(d3.max(statistics_r))
    }
    
    var stat_min = d3.min(stat_minima);
    var stat_max = d3.max(stat_maxima);
    
    //append paths to the graph for each player individually
    var n;
    var len = data.length;
    for (n=0; n < len; n++ ){
        
        //convert the data
        var player = data[n].SPIELER || data[n].TORHÜTER || data[n]['TORHÜTER*IN'];
        
        //convert dates to actual dates
        var dates = Object.keys(data[n]);
        dates.shift()
        var e;
        for (e in dates){
            dates[e] = d3.timeParse("%y_%m_%d")(dates[e])
        }
        
        //convert statistics to numbers
        var statistics = Object.values(data[n]);
        statistics.shift()
        for (e in statistics){
            statistics[e] = Number(statistics[e]);
        }
        
        //set up array for d3.line
        var xy = [];
        for(var i=0;i<dates.length;i++){
           xy.push({x:dates[i],y:statistics[i]});
        }

        //scale the range of the axes
        var x = d3.scaleTime()
            .domain(d3.extent(xy, function(d) { return d.x; }))
            .range([0, width]);
        var y = d3.scaleLinear()
            .domain([stat_min, stat_max])
            .range([height, 0]);
        
        // only on the first one, append the gridlines
        if (n==0){
            // gridlines in x axis function
            function make_x_gridlines() {		
                return d3.axisBottom(x).ticks(dates.length).tickValues(dates)
                }
            // gridlines in y axis function
            function make_y_gridlines() {
                const yAxisTicks = y.ticks().filter(tick => Number.isInteger(tick)); 
                return d3.axisLeft(y).tickValues(yAxisTicks)
                } 
            // add the X gridlines
            svg.append("g")			
                .attr("class", "grid_ips")
                .attr("transform", "translate(0," + height + ")")
                .call(make_x_gridlines()
                    .ticks()
                    .tickSize(-height)
                    .tickFormat("")
                    )
            // add the Y gridlines
            svg.append("g")			
                .attr("class", "grid_ips")
                .call(make_y_gridlines()
                    .tickSize(-width)
                    .tickFormat("")
                    )
        }
        
        //append checkboxes to div and name them according to players
        var cb_player = player.replace(/ /g,"_");
        addCheckbox(cb_player)
        
        //set up random color
        var color = d3.interpolateInferno(n*1/len);
        
        // Add the line
        svg.append("path")
            .datum(xy)
            .attr('class', 'player_stat')
            .attr('id', player.replace(/ /g,"_") + '_line')
            .attr("fill", "none")
            .attr("stroke", color)
            .attr('stroke-width', '4px')
            .on('mouseover', function(){
                    d3.select(this)
                        .attr('stroke-width', '10px').raise();
            
                    var lineID = d3.select(this).attr('id');
                    var state = d3.select(this).attr('opacity');
                    
                    if (state == 0){}
                    else{
                        d3.select('#label_' + lineID.substr(0,lineID.length - 5))
                        .style('background-color', '#ff1c73');   
                    }         
                })
            .on('mouseout', function(){
                    d3.select(this)
                        .attr('stroke-width', '4px');
            
                    var lineID = d3.select(this).attr('id');
                    var state = d3.select(this).attr('opacity');
                    
                    if (state == 0){}
                    else{
                        d3.select('#label_' + lineID.substr(0,lineID.length - 5))
                        .style('background-color', null);   
                    }
                })
            .attr("d", d3.line()
            .x(function(d) { return x(d.x) })
            .y(function(d) { return y(d.y) })
            )                        
        
        // only on the last iteration, append the axes and the buttons to show/hide all datapoints
        if (n==data.length -1){
                // gridlines in y axis function
                function make_y_gridlines() {
                    const yAxisTicks = y.ticks().filter(tick => Number.isInteger(tick)); 
                    return d3.axisLeft(y).tickValues(yAxisTicks)
                } 

                //append x-axis
                svg.append("g")
                    .attr('class', 'axes')
                    .attr("transform", "translate(0," + height + ")")
                    .call(d3.axisBottom(x)
                          .tickValues(dates)
                          .tickFormat(d3.timeFormat('%d.%m.%y')))
                    .selectAll("text")
                        .attr('class', 'x_ticks_ips')
                        .style("text-anchor", "end")
                        .attr("dx", "-.8em")
                        .attr("dy", ".15em")
                        .attr("transform", "rotate(-65)");
            
                //append y-axis
                svg.append("g")
                    .attr('class', 'axes')
                    .call(make_y_gridlines()
                        .tickFormat(d3.format('.0f')));
            
            
                // text label for the x axis
                svg.append("text")
                    .attr('class', 'axes-label')
                    .attr("transform", "translate(" + (width/2) + " ," + (height + margin.top) + ")")
                    .style("text-anchor", "middle")
                    .text("Games [dates]");
            
            
                
                //set up y axis label
                var prcnt = ['%', '%_goalie'];
                var count = ["2'", 'D', 'TF', 'V'];
            
            
                // text label for the y axis
                svg.append("text")
                    .attr('class', 'axes-label')
                    .attr("transform", "rotate(-90)")
                    .attr("y", 0 - margin.left)
                    .attr("x", 0 - (height / 2))
                    .attr("dy", "0.8em")
                    .style("text-anchor", "middle")
                    .text(function(){
                        
                        if (count.includes(stat)){
                            return 'Count'
                        }else{return 'Efficiency [%]'}
                    
                    
                        }); 

                
                //add title
                svg.append("text")
                    .attr('class', 'chart-title')
                    .attr("transform", "translate(" + (width/2) + " ," + (0-margin.top/2) + ")")
                    .attr("text-anchor", "middle")   
                    .text('Player Statistic: '+title);
            
            
            
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
                    d3.selectAll('.player_stat').attr('opacity', 1);
                }
                function uncheckAll(){
                    d3.selectAll('.checkbox_box').property('checked', false);
                    d3.selectAll('.player_stat').attr('opacity', 0);
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
    } 
}
