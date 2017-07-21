<?php

namespace Ething\Query;



class Field {
	
	private $name;
	private $type;
	private $compilfn;
	
	public function __construct($name, $type = null, $compilfn = null) {
		
		$this->name = $name;
		
		$this->type = isset($type) ? $type : '*';
		
		$this->compilfn = $compilfn;
		
	}
	
	public function type(){
		return $this->type;
	}
	
	public function compil(Operator $operator, Value $value){
		return is_callable( $this->compilfn ) ? call_user_func_array( $this->compilfn, func_get_args() ) : $operator->compil($this,$value);
	}
	
	public function __toString(){
		return $this->name;
	}
}

