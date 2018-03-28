function map() {
    if(typeof this.<KEY> === 'number') emit(1, // Or put a GROUP BY key here
         {sum: this.<KEY>, // the field you want stats for
          min: this.<KEY>,
          max: this.<KEY>,
          count:1,
          diff: 0, // M2,n:  sum((val-mean)^2)
		  minDate: this.date,
		  maxDate: this.date,
		  minId: this._id,
		  maxId: this._id,
		  startDate: this.date,
		  endDate: this.date,
    });
}