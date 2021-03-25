export function populateStats(tree){
    var keys = Object.keys(tree);
    var x;
    
    //clear dropdown first
    document.getElementById('stats').innerHTML = '';
    
    for (x in keys){
        var team = keys[x];
        var newO = document.createElement('BUTTON');
        newO.setAttribute('href',"#");
        newO.setAttribute('class',"dropdown_button")
        newO.addEventListener('click', function() {
            var selected = this.innerHTML;
            document.getElementById('dropdown_stats').innerHTML = selected
                        })
        newO.innerHTML = team;
        document.getElementById('stats').appendChild(newO);
    }
}