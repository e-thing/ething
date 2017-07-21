<?php

namespace Ething\Query;

// replace bool by boolean

/*

This class will parse a query string into a MongoDB query object used to filter a collection.


 
*/
	

class Parser {
	
	private $constants = array();
	private $fields = array();
	private $operators = array();
	
	private $fieldFallback = null;
	
	public function __construct(array $fields = array(), array $constants = array()){
		
		// set defaults operators
		$this->addOperator( array(
			
			new Operator('==', function($field,$value){
					return array(
						(string)$field => $value->is('date') ? new \MongoDB\BSON\UTCDateTime($value->getDate()->getTimestamp()*1000) : $value->getValue()
					);
				}),
			new Operator('!=', function($field,$value){
					return array(
						(string)$field => array( '$ne' => $value->is('date') ? new \MongoDB\BSON\UTCDateTime($value->getDate()->getTimestamp()*1000) : $value->getValue() )
					);
				}),
			new Operator('exists', function($field){
					return array(
						(string)$field => array( '$exists' => true )
					);
				}, '*', false),
			new Operator('is', function($field,$value){
					switch(strtolower($value->getValue())){
						case 'string':
							return array(
								(string)$field => array( '$type' => 2 )
							);
						case 'boolean':
						case 'bool':
							return array(
								(string)$field => array( '$type' => 8 )
							);
						case 'number':
							return array(
								'$or' => array(
									array( (string)$field => array( '$type' => 1 ) ),
									array( (string)$field => array( '$type' => 16 ) ),
									array( (string)$field => array( '$type' => 18 ) )
								)
							);
						case 'integer':
							return array(
								'$or' => array(
									array( (string)$field => array( '$type' => 16 ) ),
									array( (string)$field => array( '$type' => 18 ) )
								)
							);
						case 'float':
						case 'double':
							return array(
								(string)$field => array( '$type' => 1 )
							);
						case 'null':
							return array(
								(string)$field => array( '$type' => 10 )
							);
						default:
							throw new InvalidQueryException("unknown type '{$value}'",$stream);
					}
				}, '*', 'string'),
			// number or date
			new Operator('<', function($field,$value){
					return array(
						(string)$field => array( '$lt' => $value->is('date') ? new \MongoDB\BSON\UTCDateTime($value->getDate()->getTimestamp()*1000) : $value->getValue() )
					);
				}, array('integer','double','date')),
			new Operator('>', function($field,$value){
					return array(
						(string)$field => array( '$gt' => $value->is('date') ? new \MongoDB\BSON\UTCDateTime($value->getDate()->getTimestamp()*1000) : $value->getValue() )
					);
				}, array('integer','double','date')),
			// number only
			new Operator('<=', function($field,$value){
					return array(
						(string)$field => array( '$lte' => $value->getValue() )
					);
				}, array('integer','double')),
			new Operator('>=', function($field,$value){
					return array(
						(string)$field => array( '$gte' => $value->getValue() )
					);
				}, array('integer','double')),
			// string only
			new Operator('^=', function($field,$value){ // start with
					return array(
						(string)$field => array( '$regex' => '^'.$value->getValue() )
					);
				}, array('string')),
			new Operator('$=', function($field,$value){ // end with
					return array(
						(string)$field => array( '$regex' => $value->getValue().'$' )
					);
				}, array('string')),
			new Operator('*=', function($field,$value){ // containing
					return array(
						(string)$field => array( '$regex' => $value->getValue() )
					);
				}, array('string')),
			new Operator('~=', function($field,$value){ // containing word
					return array(
						(string)$field => array( '$regex' => '(^|\s)'.$value->getValue().'($|\s)' )
					);
				}, array('string'))
			
		 ));
		$this->addField($fields);
		$this->addConstant($constants);
	}
	
	
	public function addConstant($name, $value = null){
		
		if(is_array($name)){
			foreach($name as $key => $value)
				$this->constants[$key] = $value;
		}
		else 
			$this->constants[$name] = $value;
	}
	
	public function getConstant($name){
		return isset($name) ? ( isset($this->constants[$name]) ? $this->constants[$name] : null ) : array_values($this->constants);
	}
	
	public function addField($field){
		if(is_array($field)){
			foreach($field as $value)
				$this->addField($value);
		}
		else if($field instanceof Field)
			$this->fields[(string)$field] = $field;
	}
	
	public function getField($name){
		return isset($name) ? ( isset($this->fields[$name]) ? $this->fields[$name] : null ) : array_values($this->fields);
	}
	
	public function addOperator($operator){
		if(is_array($operator)){
			foreach($operator as $value)
				$this->addOperator($value);
		}
		else if($operator instanceof Operator)
			$this->operators[(string)$operator] = $operator;
	}
	
	public function getOperator($syntax){
		return isset($syntax) ? ( isset($this->operators[$syntax]) ? $this->operators[$syntax] : null ) : array_values($this->operators);
	}
	
	
	public function setFieldFallback($fallback){
		$this->fieldFallback = is_callable($fallback) ? $fallback : null;
	}
	
	/*
	* Entry point
	*/
	public function parse($query){
		$stream = new Stream($query);
		return $this->parseExpression($stream);
	}
	
	
	
	private function parseField(Stream &$stream){
		$stream->skipSpace();
		if($field = $stream->read('/[a-z0-9\.\-_]+/i')){
			if(array_key_exists($field, $this->fields)){
				return $this->fields[$field];
			}
			else{
				if($this->fieldFallback){
					$f = call_user_func($this->fieldFallback, $field);
					if($f instanceof Field)
						return $f;
				}
				throw new InvalidQueryException("unknown field '{$field}'",$stream);
			}
		}
		else
			throw new InvalidQueryException('expected a field',$stream);
	}
	
	
	private function parseOperator(Stream &$stream){
		$stream->skipSpace();
		if(($op = $stream->read('/[\=\!\^\>\<\$\*~]+/')) || ($op = $stream->readWord())){
			if(array_key_exists($op, $this->operators)){
				return $this->operators[$op];
			}
			else
				throw new InvalidQueryException("unknown operator '{$op}'",$stream);
		}
		else
			throw new InvalidQueryException("expected an operator",$stream);
	}
	
	private function parseValue(Stream &$stream){
		$stream->skipSpace();
		
		// try to get string (double quotes or simple quotes)
		if ( ($v = $stream->read('/^(?:\"([^\"]*(?:\"\"[^\"]*)*)\")/')) || ($v = $stream->read('/^(?:\'([^\']*(?:\'\'[^\']*)*)\')/')) ){
			// quoted string
			$r = substr($v, 1, -1); // remove the quotes
			if($v[0] === '"'){
				$r = \stripcslashes($r);
			}
			return new Value($r);
		}
		else {
			$v = $stream->read('/[a-z0-9\.\-_+]+/i');
			
			// number ? (integer or float)
			if(is_numeric($v)){
				return new Value($v + 0);
			}
			// boolean ?
			else if( preg_match('/^(true|false)$/i',$v) ){
				return new Value((bool) preg_match('/true/i',$v));
			}
			// maybe a CONSTANT
			else if(array_key_exists($v, $this->constants)){
				return new Value($this->constants[$v]);
			}
			else
				throw new InvalidQueryException("invalid value '{$v}'",$stream);
		}
		
	}
	
	/*
	 parse a Field-Operator-Value expression
	*/
	private function parseFOV(Stream &$stream){
		
		if($stream->read('/^\s*not($|\s+)/i')){
			return array( '$nor' => array($this->parseFOV($stream)) );
		}
		
		$field = $this->parseField($stream);
		$op = $this->parseOperator($stream);
		$value = $op->hasValue() ? $this->parseValue($stream) : new Value();
		
		if(!$op->accept($field, $value)){
			throw new InvalidQueryException("the operator '{$this}' is invalid");
		}
		
		try {
			$compiled = $field->compil($op,$value);
		}
		catch(\Exception $e){
			throw new InvalidQueryException($e->getMessage(),$stream);
		}
		
		return $compiled;
	}
	
	
	
	/*
	 * Parse a FOV or a enclosed expression
	*/
	private function parseFragment(Stream &$stream){
		if($stream->read('/^\s*\(/')){
			// start enclosure
			$f = $this->parseExpression($stream);
			
			// must be followed by a ')'
			if(!$stream->read('/^\s*\)/'))
				throw new InvalidQueryException("expected a ')'",$stream);
			
		}
		else
			$f = $this->parseFOV($stream);
			
		return $f;
	}
	
	private function parseExpression(Stream &$stream){
		
		$stack = array();
		
		$stream->skipSpace();
		
		if(!$stream->length() || $stream->match('/^\)/'))
			throw new InvalidQueryException('empty expression',$stream);
		
		// get the first fragment
		$stack[] = $this->parseFragment($stream);
		
		
		// search for other FOV expressions separated by a logical operator
		while($stream->length()){
			
			$stream->skipSpace();
			
			if(!$stream->length() || $stream->match('/^\)/'))
				break; // the end
			
			// search for a logical operator
			if($logic = $stream->read('/^(and|or)($|\s+)/i')){
				$stack[] = strtolower(trim($logic));
			}
			else
				throw new InvalidQueryException('waiting for a logical operator',$stream);
			
			// search for a fragment
			$stack[] = $this->parseFragment($stream);
			
		}
		
		//compilation of the stack
		$logicPrecedence = array('and','or');
		$logicIndex = 0;
		while(count($stack)>1){
			
			$currentLogic = $logicPrecedence[$logicIndex];
			
			for($i=0; $i<count($stack); $i++){
				if($stack[$i] === $currentLogic){
					$exp = array(
						'$'.$currentLogic => array( $stack[$i-1] , $stack[$i+1] )
					);
					
					array_splice ( $stack, $i-1, 3, array($exp) );
					
					$i--;
				}
			}
			
			$logicIndex++;
			
			if($logicIndex == count($logicPrecedence)){
				if(count($stack)>1)
					throw new InvalidQueryException('error');
				break;
			}
		}
		
		return $stack[0];
		
	}
	
}
