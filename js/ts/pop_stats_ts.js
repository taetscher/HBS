export function populateStats(tree){
    var keys = Object.keys(tree);
    var x;
    
    //clear dropdown first
    document.getElementById('stats').innerHTML = '';
    
    for (x in keys){
        var team = keys[x];
        var newO = document.createElement('BUTTON');
        newO.setAttribute('href',"#");
        newO.setAttribute('id',"game");
        newO.setAttribute('class',"dropdown_button")
        newO.addEventListener('click', function() {
            var selected = this.innerHTML;
            document.getElementById('dropdown_stats').innerHTML = selected
                        })
        newO.innerHTML = team;
        document.getElementById('stats').appendChild(newO);
    }
    
    //add a first one, combining all of them
    var all_games = document.createElement('BUTTON');
    all_games.setAttribute('href',"#");
    all_games.setAttribute('class',"dropdown_button")
    all_games.setAttribute('id',"all_games");
    all_games.addEventListener('click', function() {
        var selected = this.innerHTML;
        document.getElementById('dropdown_stats').innerHTML = selected
                    })
    all_games.innerHTML = 'All Games Combined';
    document.getElementById('stats').prepend(all_games);
    
}