function reduce(key, values) {
    var a = values[0]; // will reduce into here
    for (var i=1/*!*/; i < values.length; i++){
        var b = values[i]; // will merge 'b' into 'a'

        // temp helpers
        var delta = a.sum/a.count - b.sum/b.count; // a.mean - b.mean
        var weight = (a.count * b.count)/(a.count + b.count);
        
        // do the reducing
        a.diff += b.diff + delta*delta*weight;
        a.sum += b.sum;
        a.count += b.count;
		
		if(b.min<a.min){
			a.min = b.min;
			a.minDate = b.minDate;
			a.minId = b.minId;
		}
		if(b.max>a.max){
			a.max = b.max;
			a.maxDate = b.maxDate;
			a.maxId = b.maxId;
		}
		if(b.startDate<a.startDate){
			a.startDate = b.startDate;
		}
		if(b.endDate>a.endDate){
			a.endDate = b.endDate;
		}
		
    }
	
    return a;
}