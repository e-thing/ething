<?php

namespace Ething\Query;



/*

This class will parse a query string into a MongoDB query object used to filter a collection.


 
*/
	

class Parser {
	
	private static $operators = null;
	
	private $constants = array();
	private $fields = array();
	
	static private function load(){
		
		if(isset(static::$operators))
			return;
		
		
		static::$operators = array(
			
			'==' => array(
				'accept' => '*',
				'compil' => function($field,$value){
					return array(
						$field => $value
					);
				}
			),
			'!=' => array(
				'accept' => '*',
				'compil' => function($field,$value){
					return array(
						$field => array( '$ne' => $value )
					);
				}
			),
			'is' => array(
				'accept' => '*',
				'compil' => function($field,$value){
					switch(strtolower($value)){
						case 'string':
							return array(
								$field => array( '$type' => 2 )
							);
						case 'boolean':
						case 'bool':
							return array(
								$field => array( '$type' => 8 )
							);
						case 'number':
							return array(
								'$or' => array(
									array( $field => array( '$type' => 1 ) ),
									array( $field => array( '$type' => 16 ) ),
									array( $field => array( '$type' => 18 ) )
								)
							);
						case 'integer':
							return array(
								'$or' => array(
									array( $field => array( '$type' => 16 ) ),
									array( $field => array( '$type' => 18 ) )
								)
							);
						case 'float':
						case 'double':
							return array(
								$field => array( '$type' => 1 )
							);
						default:
							throw new InvalidQueryException("unknown type '{$value}'",$stream);
					}
				}
			),
			
			// number or date
			'<' => array(
				'accept' => array('integer','double','date'),
				'compil' => function($field,$value){
					return array(
						$field => array( '$lt' => $value )
					);
				}
			),
			'>' => array(
				'accept' => array('integer','double','date'),
				'compil' => function($field,$value){
					return array(
						$field => array( '$gt' => $value )
					);
				}
			),
			
			// number only
			'<=' => array(
				'accept' => array('integer','double'),
				'compil' => function($field,$value){
					return array(
						$field => array( '$le' => $value )
					);
				}
			),
			'>=' => array(
				'accept' => array('integer','double'),
				'compil' => function($field,$value){
					return array(
						$field => array( '$ge' => $value )
					);
				}
			),
			
			// string only
			'^=' => array(
				'accept' => array('string'), // start with
				'compil' => function($field,$value){
					return array(
						$field => array( '$regex' => '^'.$value )
					);
				}
			),
			'$=' => array(
				'accept' => array('string'), // end with
				'compil' => function($field,$value){
					return array(
						$field => array( '$regex' => $value.'$' )
					);
				}
			),
			'*=' => array(
				'accept' => array('string'), // containing
				'fct' => function($a,$b){
					return strpos($a,$b)!==false;
				},
				'compil' => function($field,$value){
					return array(
						$field => array( '$regex' => $value )
					);
				}
			),
			'~=' => array(
				'accept' => array('string'), // containing word
				'compil' => function($field,$value){
					return array(
						$field => array( '$regex' => '(^|\s)'.$value.'($|\s)' )
					);
				}
			)
			
			
		);
	}
	
	
	public function __construct(array $fields = array()){
		static::load();
		
		$this->fields = $fields;
	}
	
	
	public function addConstant($name, $value){
		$this->constants[$name] = $value;
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
				return $field;
			}
			else
				throw new InvalidQueryException("unknown field '{$field}'",$stream);
		}
		else
			throw new InvalidQueryException('expected a field',$stream);
	}
	
	
	private function parseOperator(Stream &$stream){
		$stream->skipSpace();
		if(($op = $stream->read('/[\=\!\^\>\<\$\*~]+/')) || ($op = $stream->readWord())){
			if(array_key_exists($op, static::$operators)){
				return $op;
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
			return substr($v, 1, -1); // remove the quotes
		}
		else {
			$v = $stream->read('/[a-z0-9\.\-_+]+/i');
			
			// number ? (integer or float)
			if(is_numeric($v)){
				return $v + 0;
			}
			// boolean ?
			else if( preg_match('/^(true|false)$/i',$v) ){
				return (bool) preg_match('/true/i',$v);
			}
			// maybe a CONSTANT
			else if(array_key_exists($v, $this->constants)){
				return $this->constants[$v];
			}
			else
				throw new InvalidQueryException("invalid value '{$v}'",$stream);
		}
		
	}
	
	/*
	 parse a Field-Operator-Value expression
	*/
	private function parseFOV(Stream &$stream){
		
		$field = $this->parseField($stream);
		$op = $this->parseOperator($stream);
		$value = $this->parseValue($stream);
		
		$opDesc = static::$operators[$op];
		$fieldDesc = $this->fields[$field];
		
		$fieldType = $fieldDesc['type'];
		
		// rename the field before compilation !
		if(isset($fieldDesc['name']))
			$field = $fieldDesc['name'];
		
		$constraints = array();
		
		if($fieldType == '*'){
			
			// special case, the field type is unknown !
			
			// check that the operator is compatible with the type of the value
			if($opDesc['accept'] != '*'){
				$valueType = gettype($value);
				if(!in_array($valueType,$opDesc['accept']))
					throw new InvalidQueryException("the value '{$value}' is not a {$valueType}",$stream);
				
				// the value can be anything ...
				// but add some constraints in order to avoid errors
				// for instance, the operator $ge will fail on string and fire an error
				// so check the type of the value before compare the value !
				
				$constraints = array();
				
				foreach($opDesc['accept'] as $type){
					switch($type){
						case 'string':
							$constraints[] = array( $field => array( '$type' => 2 ) );
							break;
						case 'bool':
							$constraints[] = array( $field => array( '$type' => 8 ) );
							break;
						case 'double':
							$constraints[] = array( $field => array( '$type' => 1 ) );
							break;
						case 'integer':
							$constraints[] = array( $field => array( '$type' => 16 ) );
							$constraints[] = array( $field => array( '$type' => 18 ) );
							break;
						case 'date':
							$constraints[] = array( $field => array( '$type' => 9 ) );
							break;
						default:
							throw new InvalidQueryException("error",$stream); // internal error
					}
				}
				
				if(count($constraints)>1){
					$constraints = array(
						'$or' => $constraints
					);
				}
			}
			
			
		}
		else {
			
			// the type of the field is known !
		
			// the operator must be compatible with the type of the field ?
			if($opDesc['accept'] != '*' && !in_array($fieldType,$opDesc['accept']))
				throw new InvalidQueryException("the operator '{$op}' does not accept {$fieldType}",$stream);
			
			// is the value also compatible with the type given by the field ?
			switch($fieldType){
				case 'string':
				case 'integer':
				case 'double':
				case 'bool':
					if(gettype($value) != $fieldType) // php type
						throw new InvalidQueryException("the value '{$value}' is not a {$fieldType}",$stream);
					break;
				case 'number':
					if(!is_int($value) && !is_float($value))
						throw new InvalidQueryException("the value '{$value}' is not a number",$stream);
					break;
				case 'date':
					$date = \date_create( $value );
					if($date === false)
						throw new InvalidQueryException("invalid date '{$value}'",$stream);
					$value = new \MongoDate($date->getTimestamp());
					break;
				default:
					throw new InvalidQueryException("error",$stream);
			}
		}
		
		$compiled = isset($fieldDesc['compil']) ? $fieldDesc['compil']($op,$value) : $opDesc['compil']($field,$value);
		
		return array_merge( $compiled , $constraints );
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
