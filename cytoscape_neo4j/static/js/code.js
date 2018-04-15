function query(){
    words = document.getElementById('words').value;
  $.get('/graph?words='+words, function(result) {
    var style = [
      { selector: 'node[label = "Word"]', css: {'background-color': '#6FB1FC'}}
    ];

    var cy = cytoscape({
      container: document.getElementById('cy'),
      style: style,
      layout: { name: 'cose', fit: false },      
      elements: result.elements
    });
  }, 'json');  
};