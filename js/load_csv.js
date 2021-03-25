export function loadCSV(dataURL){
    var data = d3.csv(dataURL);
    return data
};