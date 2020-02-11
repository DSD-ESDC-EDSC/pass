function downloadData(data) {
  /*data = JSON.parse(data);*/
  console.log(data);

  let csvContent = ConvertToCSV(data["features"]);

  /*var encodedUri = encodeURI(csvContent);
  window.open(encodedUri);*/

  var csvData = new Blob([csvContent], {type: 'text/csv;charset=utf-8;'});
  //IE11 & Edge
  if (navigator.msSaveBlob) {
    navigator.msSaveBlob(csvData, 'pass_scores.csv');
  } else {
    //In FF link must be added to DOM to be clicked
    var link = document.createElement('a');
    link.href = window.URL.createObjectURL(csvData);
    link.setAttribute('download', 'pass_scores.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}

function ConvertToCSV(objArray) {
  var array = typeof objArray != 'object' ? JSON.parse(objArray) : objArray;
  var str = '';
  var keys = Object.keys(array[0]["properties"]);

  for (var i = 0; i < keys.length; i++){
    str += keys[i];
    if (i != keys.length - 1) {
      str += ',';
    }else{
      str += '\r\n';
    }
  }
  for (var i = 0; i < array.length; i++) {
    var line = '';
    for (key in array[i]["properties"]){
      line += array[i]["properties"][key] + ',';
    }
    str += line + '\r\n';
  }
  return str;
}
