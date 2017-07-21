<?php


namespace Ething\Action;
	
class TableStatistics extends Action {
	
	
	static public function validate(array &$attributes, array $context){
		
		$attributes = array_merge(
			array( 
				'resource' => null, // table where the data are stored
				'field' => null, // the table field to make the statistics
				'dataset' => null, // the amount of points or the duration(in seconds) to take into account for the statistics. If not set, all the data will be taken into account.
				'destination' => null // table where to store the computed statistics
			),
			$attributes
		);
		
		foreach(array_keys($attributes) as $key){
			
			switch($key){
				
				case 'resource':
					
					if(!is_string($attributes[$key]))
						throw new \Exception("field '{$key}' must be a string.");
					
					$resource = $context['ething']->get($attributes[$key]);
					if(!$resource)
						throw new \Exception("the resource with id '{$attributes[$key]}' does not exist.");
					
					if($resource->baseType() != 'Table')
						throw new \Exception("the resource with id '{$attributes[$key]}' must be a Table.");
					
					break;
				
				case 'destination':
					
					if(!is_string($attributes[$key]))
						throw new \Exception("field '{$key}' must be an id.");
					
					$resource = $context['ething']->get($attributes[$key]);
					if(!$resource)
						throw new \Exception("the destination with id '{$attributes[$key]}' does not exist.");
					
					if($resource->baseType() != 'Table')
						throw new \Exception("the destination with id '{$attributes[$key]}' must be a Table.");
					
					break;
				
				case 'field':
					
					if(empty($attributes[$key]) || !is_string($attributes[$key]))
						throw new \Exception("field '{$key}' must be a non empty string.");
					
					break;
				
				case 'dataset':
					
					if(!is_integer($attributes[$key]))
						throw new \Exception("field '{$key}' must be a positive integer representing a number of seconds or a negative integer representing a number of rows. 0 means all the data.");
					
					break;
				
				default:
					throw new \Exception("field '{$key}' unknown.");
			}
			
		}
		
		return true; 
	}
	
	
	protected function call(\Ething\Event\Signal $signal){
		
		$table = $this->ething()->get( $this->resource );
		if(!$table)
			throw new \Ething\InvalidRuleException("The input table #{$this->resource} does not exist any more");
		
		$destination = $this->ething()->get( $this->destination );
		if(!$destination)
			throw new \Ething\InvalidRuleException("The output resource #{$this->destination} does not exist any more");
		
		
		$field = $this->field;
		
		if(empty($this->dataset) || $this->dataset<0)
			$data = $table->select(intval($this->dataset),null,['date',$field]);
		else
			$data = $table->select(0,null,['date',$field],array(
				'date' => array(
					'$gt' => (new \MongoDB\BSON\UTCDateTime((time() - $this->dataset)*1000))
				)
			));
		
		
		// make the statistics
		$n = 0;
		$startDate = null;
		$endDate = null;
		$sum = 0;
		$sumSquare = 0;
		$min = null;
		$max = null;
		$minDate = null;
		$maxDate = null;
		foreach($data as $item){
			if(isset($item->$field)){
				$value = $item->$field;
				
				if(is_float($value) || is_int($value)){
					$date = $item->date;
					
					if($n===0) $startDate = $date;
					
					$n++;
					$sum += $value;
					$sumSquare += $value*$value;
					
					if($min===null || $value<$min) {
						$min = $value;
						$minDate = $date;
					}
					if($max===null || $value>$max) {
						$max = $value;
						$maxDate = $date;
					}
				}
			}
		}
		if(isset($date)) $endDate = $date;
		
		$mean = $n != 0 ? ($sum / $n) : null;
		$sd = $n != 0 ? sqrt( ($sumSquare/$n) - ($mean*$mean) ) : null;
		
		$statistics = array(
			'length' => $n,
			'startDate' => $startDate,
			'endDate' => $endDate,
			'mean' => $mean,
			'minDate' => $minDate,
			'min' => $min,
			'maxDate' => $maxDate,
			'max' => $max,
			'sd' => $sd
		);
		
		$destination->insert($statistics);
		
	}
	
}


