import {getTree} from '../get_tree.js'
import {populateDropdownTS} from './pop_teams_ips.js'
import {populateSeasons} from './pop_seasons_ips.js'
import {populateStats} from './pop_stats_ips.js'
import {visualizeIPS} from './visualize_ips.js'
import {addHiddenScript} from '../add_hidden_script.js'

document.getElementById("dropdown_stats").style.visibility= "hidden" ;
var resize_timeout;

//add hidden scripts to store JSON data
addHiddenScript('seasons_dict');
addHiddenScript('stats_dict');

wrapper();

//every time the window is resized, draw again
window.addEventListener('resize', function(){
    resize_timeout = setTimeout(visualizeIPS, 500)
});

async function wrapper(){
    /*wrapper function to force sync ecexution of async functions
    */
    
    //populate the team selection dropdown
    var treeAtMaster = "https://api.github.com/repos/taetscher/HBS/git/trees/master"
    var basetree = await getTree(treeAtMaster)
    var output_csv = await getTree(basetree.output_csv)
    var teams = await getTree(output_csv.progress_data)
    populateDropdownTS(teams);

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
            //initiate the display of data via d3.js
            visualizeIPS()
        })
    
}
