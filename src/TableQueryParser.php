<?php
	
	
	namespace Ething;
	
	
	class TableQueryParser extends Query\Parser {
		
		
		public function __construct() {
			
			parent::__construct(array(
				new Query\Field('id', 'string', function($op,$value){
					return (new Query\Field('_id'))->compil($op,$value);
				}),
				new Query\Field('date', 'date')
			));
			
			$this->setFieldFallback(function($field){
				return new Query\Field($field);
			});
				
		}
		
		
		static public function check($expr, &$error = null){
			$error = false;
			try {
				$parser = new TableQueryParser();
				$parser->parse($expr);
				return true;
			} catch(\Exception $e){
				$error = $e->getMessage();
				return false;
			}
		}
		
		
		
		
	}
	
	
	
	
	
	
	
	
	
	
	