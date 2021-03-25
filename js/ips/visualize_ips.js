import {loadCSV} from '../load_csv.js';
import {vizClean} from './visualize_clean_data.js';
import {vizUnClean} from './visualize_unclean_data.js';

export function visualizeIPS(){
    
    //remove existing visualization
    $("#chart").html("");
    $("#checkboxes").html("");
    
    //construct an url to the base data
    var ts_baseurl = "https://raw.githubusercontent.com/taetscher/handballStats/master/output_csv/progress_data/";
    var team = document.getElementById('dropdown_teams').innerHTML;
    var season = document.getElementById('dropdown_seasons').innerHTML;
    var stat = document.getElementById('dropdown_stats').innerHTML;
    var dataURL = ts_baseurl+team+"/"+season+"/"+stat;
    dataURL = encodeURI(dataURL)
    console.log(dataURL)
    
    //load the data
    loadCSV(dataURL).then(function (data){

        //check which viz-mode is needed
        var unclean = ['7M', '7M_goalie', 'P-W_goalie', 'TORE'];
        
        if (unclean.includes(stat)){
            vizUnClean(data)
            }
        else {
            vizClean(data)
            }
        }
    );
}