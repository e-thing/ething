(function (H) {
    

    H.wrap(H.Chart.prototype, 'init', function (proceed, chartOptions, callback) {
		
		var dfrs = [];
		
		chartOptions.series = chartOptions.series || [];
		
		
		chartOptions.series.forEach(function(serie, index){
			
			if(!Array.isArray(serie.data)){
				
				dfrs.push(
					$.when(serie.data).done(function(data){
						
						chartOptions.series[index].data = data;
						
					}).fail(function(err){
						console.error('failed to load data for series['+index+']', err);
					})
				);
				
			}
			
		});
		
		
		var args = Array.prototype.slice.call(arguments, 1);
		
		if(dfrs.length){
			var self = this;
			$.when.apply($, dfrs).done(function(){
				proceed.apply(self, args);
			});
		} else {
			proceed.apply(this, args);
		}
		
		
        
    });
    
	


   
}(Highcharts));