<?php
	
	
	namespace Ething;
	
	
	class ResourceQueryParser extends Query\Parser {
		
		
		public function __construct(Ething $ething) {
			
			$createdByField = new Query\Field('createdBy.id', 'string');
			parent::__construct( array(
				new Query\Field('type', 'string'),
				new Query\Field('name', 'string'),
				new Query\Field('mime', 'string'),
				new Query\Field('id', 'string'),
				new Query\Field('location.latitude', 'double'),
				new Query\Field('location.longitude', 'double'),
				new Query\Field('location.altitude', 'double'),
				new Query\Field('expireAfter', 'integer'),
				new Query\Field('createdDate', 'date'),
				new Query\Field('modifiedDate', 'date'),
				new Query\Field('lastSeenDate', 'date'),
				new Query\Field('createdDate', 'date'),
				new Query\Field('createdBy', 'string', function($op,$value) use ($createdByField) {
						// shortcut
						return $createdByField->compil($op,$value);
					}),
				new Query\Field('createdBy.type', 'string'),
				$createdByField,
				new Query\Field('length', 'integer'),
				new Query\Field('size', 'integer'),
				new Query\Field('description', 'string'),
				new Query\Field('battery', 'double'),
				new Query\Field('hasThumbnail', 'bool', function($op,$value){
						
						switch((string)$op){
							case '!=':
								$value = !$value;
							case '==':
								break;
							default:
								throw new \Exception("the operator '{$op}' is not accepted with the field 'hasThumbnail'");
						}
						
						return $value ? array(
							'_thumb' => array( '$ne' => null )
						) : array(
							'_thumb' => null
						);
					}),
				new Query\Field('hasIcon', 'bool', function($op,$value){
							
						switch((string)$op){
							case '!=':
								$value = !$value;
							case '==':
								break;
							default:
								throw new \Exception("the operator '{$op}' is not accepted with the field 'hasIcon'");
						}
						
						return $value ? array(
							'_icon' => array( '$ne' => null )
						) : array(
							'_icon' => null
						);
					})
					
					
			) );
			
			$this->setFieldFallback(function($field){
				
				if(preg_match('/^data\.(.+)$/', $field, $matches)){
					return new Query\Field($field);
				}
				if(preg_match('/^keys\.(.+)$/', $field, $matches)){
					return new Query\Field($field,'integer');
				}
				
			});
				
		}
		
		
		static public function check(Ething $ething, $expr, &$error = null){
			$error = false;
			try {
				$parser = new ResourceQueryParser($ething);
				$parser->parse($expr);
				return true;
			} catch(\Exception $e){
				$error = $e->getMessage();
				return false;
			}
		}
		
		
	}
	
	
	
	
	
	
	
	
	
	
	