import {getTree} from '../get_tree.js'
import {populateDropdownTS} from './pop_teams_ts.js'
import {populateSeasons} from './pop_seasons_ts.js'
import {populateStats} from './pop_stats_ts.js'
import {visualizeTS, visualizeTS_allGames} from './visualize_ts.js'
import {addHiddenScript} from '../add_hidden_script.js'

document.getElementById("dropdown_stats").style.visibility= "hidden";
var resize_timeout;

//add hidden scripts to store JSON data
addHiddenScript('seasons_dict');
addHiddenScript('stats_dict');

wrapper();

//when window is resized, wait for 500ms and draw agiain
window.addEventListener('resize', function(){
    resize_timeout = setTimeout(draw, 500)
})

async function wrapper(){
    /**wrapper function to force synchronous execution of async code
    */

    //populate the team selection dropdown
    var treeAtMaster = "https://api.github.com/repos/taetscher/handballStats/git/trees/master"
    var basetree = await getTree(treeAtMaster)
    var output_csv = await getTree(basetree.output_csv)
    var teams = await getTree(output_csv.gameProgressions)
    populateDropdownTS(teams)
    
    //populate the season selection dropdown
    var team = document.getElementById('teams');
    team.addEventListener('click', async function(){
        var selected = document.getElementById('dropdown_teams').innerHTML;
        var seasons = await getTree(teams[selected]);    
        document.getElementById('seasons_dict').innerHTML = JSON.stringify(seasons);
        populateSeasons(seasons);
        })

    //populate the stat selection dropdown
    var season = document.getElementById('seasons');
    season.addEventListener('click', async function(){
        var seasons = JSON.parse(document.getElementById('seasons_dict').innerHTML);
        var selected = document.getElementById('dropdown_seasons').innerHTML;
        var stats = await getTree(seasons[selected]);
        document.getElementById('stats_dict').innerHTML = JSON.stringify(stats);
        populateStats(stats);
        document.getElementById("dropdown_stats").style.visibility= "visible" ;
        team.addEventListener('click', function(){
                document.getElementById("dropdown_stats").style.visibility= "hidden" ;
            })
        })

    //get the choice of document
    var choice = document.getElementById('stats');
    choice.addEventListener('click', function(){
            draw();
        })
    
}

function draw(){
    //initiate the display of data via d3.js
    var selection = document.getElementById('dropdown_stats').innerHTML;

    // if all games are selected, draw all of them on the same canvas
    if (selection === 'All Games Combined'){
        var x;
        var values = document.getElementById('stats').getElementsByTagName('BUTTON');

        //get all games possible
        var to_draw = []
        for (x in values){
            var game = values[x].innerHTML
            if (game === 'All Games Combined'){}
            else if (game == undefined){}
            else to_draw.push(game)
        }

        //visualize all games
        visualizeTS_allGames(to_draw)

    }
    // visualize single game
    else {visualizeTS()}
}