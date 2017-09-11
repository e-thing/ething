(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define([], factory);
    } else {
        // Browser globals
        root.CSV = factory();
    }
}(this, function () {
	
	
	var CSV = {
		extensions: ['csv','tsv','tab','txt'],
		
		parse: function(content,delimiter,limit){
			
			if(!content.length) return [];
			
			// Check to see if the delimiter is defined. If not,
			// then default to comma.
			if(!delimiter){
				if(!(delimiter = CSV.getDelimiter(content))) // auto determine
					throw 'invalid CSV content';
			}

			// Create a regular expression to parse the CSV values.
			var objPattern = new RegExp(
				(
					// Delimiters.
					"(\\" + delimiter + "|\\r?\\n|\\r|^)" +

					// Quoted fields.
					"(?:\"([^\"]*(?:\"\"[^\"]*)*)\"|" +

					// Standard fields.
					"([^\"\\" + delimiter + "\\r\\n]*))"
				),
				"gi"
			);


			// Create an array to hold our data. Give the array
			// a default empty first row.
			var arrData = [[]];

			// Create an array to hold our individual pattern
			// matching groups.
			var arrMatches = null;


			// Keep looping over the regular expression matches
			// until we can no longer find a match.
			var line = 0, prevEmptyField = false;
			while (arrMatches = objPattern.exec( content )){
				
				// Get the delimiter that was found.
				var strMatchedDelimiter = arrMatches[ 1 ];

				// Check to see if the given delimiter has a length
				// (is not the start of string) and if it matches
				// field delimiter. If id does not, then we know
				// that this delimiter is a row delimiter.
				if (
					strMatchedDelimiter.length &&
					strMatchedDelimiter !== delimiter
					){
					
					if(prevEmptyField)
						arrData[ arrData.length - 1 ].pop();
					
					line++;
					
					if(limit && line>=limit)
						break;
					
					// Since we have reached a new row of data,
					// add an empty row to our data array.
					arrData.push( [] );

				}
				
				prevEmptyField = false;
				
				var strMatchedValue;

				// Now that we have our delimiter out of the way,
				// let's check to see which kind of value we
				// captured (quoted or unquoted).
				if (arrMatches[2]){

					// We found a quoted value. When we capture
					// this value, unescape any double quotes.
					strMatchedValue = arrMatches[ 2 ].replace(
						new RegExp( "\"\"", "g" ),
						"\""
						);

				} else {

					// We found a non-quoted value.
					if(/^\s*[-+]?\d*\.?\d+([eE][-+]?\d+)?\s*$/.test(arrMatches[ 3 ])){
						// number
						strMatchedValue = parseFloat(arrMatches[ 3 ]);
					}
					else if(/^\s*(true|false)\s*/i.test(arrMatches[ 3 ])){
						// boolean
						strMatchedValue = /true/i.test(arrMatches[ 3 ]);
					}
					else {
						// string
						strMatchedValue = arrMatches[ 3 ];
						if(/^\s*$/.test(strMatchedValue))
							prevEmptyField = true;
					}

				}


				// Now that we have our value string, let's add
				// it to the data array.
				arrData[ arrData.length - 1 ].push( strMatchedValue );
				
			}
			
			
			// Return the parsed data + remove empty lines
			return arrData.filter(function(d){
				return d.length>0;
			});
			
		},
		
		getDelimiter: function(content){
			var delimiters = [',', ';', '\t', '|', ':'], best = null, colmax=0;
			
			for(var i=0; i<delimiters.length; i++){
				
				// return the number of columns or false if an error occurs
				var ncol = CSV.parse(content,delimiters[i],5).reduce(function(ncol, fields, index, array){
					if(index===0)
						ncol = fields.length;
					return (ncol===false || ncol != fields.length) ? false : ncol;
				},false);
				
				if(ncol!==false && ncol>colmax){
					best = delimiters[i];
					colmax = ncol;
				}
				
			}
			
			return best;
		}
	};
	
	
	return CSV;
	
}));