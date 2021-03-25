//write function to add hidden divs with a specific class, see issue #29
export function addHiddenScript(id){
    var div = document.createElement('script');
    div.setAttribute('type', 'text/json')
    div.setAttribute('class', 'hidden')
    div.setAttribute('id', id)
    var author = document.getElementById("author");
    var footer = document.getElementById("footer");
    footer.insertBefore(div, author)
};