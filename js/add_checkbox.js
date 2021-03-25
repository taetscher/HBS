export function addCheckbox(id) { 
        var myDiv = document.getElementById("checkboxes");

        var boxDiv = document.createElement('a')
        boxDiv.className = 'checkbox';

        // creating checkbox element 
        var checkbox = document.createElement('input'); 

        // Assigning the attributes 
        // to created checkbox 
        checkbox.type = "checkbox"; 
        checkbox.className = 'checkbox_box';
        checkbox.id = "checkbox_"+id; 
        checkbox.checked = true;

        // creating label for checkbox 
        var label = document.createElement('label');
        label.id = 'label_' + id

        // appending the created text to  
        // the created label tag 
        label.appendChild(document.createTextNode(id.replace(/_/g," "))); 

        // appending the checkbox 
        // and label to a-tag
        boxDiv.appendChild(checkbox); 
        boxDiv.appendChild(label); 

        //appending a-tag to div
        myDiv.appendChild(boxDiv);
        
        //connect checkboxes with lines
        d3.select("#checkbox_"+id).on('change', function(){
            
                            var state = d3.select(this).property('checked')
                            
                            if (state == false){
                                d3.select('#' + id + '_line')
                                .attr('opacity', 0)
                            }else{
                                d3.select('#' + id + '_line')
                                .attr('opacity', 1)
                            }
            })
                            
                            
                            
    } 

export function addCheckbox_ts(id, color, q) { 
        
        var myDiv = document.getElementById("checkboxes");

        var boxDiv = document.createElement('a')
        boxDiv.className = 'checkbox';

        // creating checkbox element 
        var checkbox = document.createElement('input'); 
    
        // creating label for checkbox 
        var label = document.createElement('label');
        label.id = 'label_' + id

        // appending the created text to  
        // the created label tag 
        label.appendChild(document.createTextNode(id.replace(/_/g," ").slice(0,-4))); 
        
        // Assigning the attributes 
        // to created checkbox 
        checkbox.type = "checkbox"; 
        checkbox.className = 'checkbox_box';
        checkbox.id = "checkbox_"+id; 
        checkbox.setAttribute('data-color', color);
        checkbox.checked = true;

        // appending the checkbox 
        // and label to a-tag
        boxDiv.appendChild(checkbox); 
        boxDiv.appendChild(label); 

        //appending a-tag to div
        myDiv.appendChild(boxDiv);
        
        //connect checkboxes with lines
        d3.select("#checkbox_"+id).on('change', function(){
            
                            var state = d3.select(this).property('checked')
                            
                            if (state == false){
                                d3.select('#'+ 'line_' + q )
                                    .attr('opacity', 0)

                            }else{
                                d3.select('#'+ 'line_' + q )
                                    .attr('opacity', 1)

                            }
            })        
    } 