export async function getURL(theUrl){
    const data = await fetch(theUrl).then(function(response){
        const json = response.json();
        return json
    })
    return data
};


export async function getTree(theUrl){
    var response = await getURL(theUrl);
    var x = 0;
    var links = {};
    for (x in response['tree']) {
        var path = response['tree'][x]['path'];
        links[path]= response['tree'][x]['url']
    }
    return links
};