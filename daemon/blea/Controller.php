<?php


namespace Ething\Blea;

use \Ething\Ething;
use \Ething\Device\BleaGateway;
use \Ething\Event;


abstract class Controller {
	
	public $gateways = array();
	
	public $ething = null;
	
	public $options = array();
	
	public function __construct(Ething $ething, array $options = array()){
		
		$this->ething = $ething;
		$this->options = array_replace_recursive($this->options, $options);
		
	}
	
	public function startGateway($id){
		
		$this->stopGateway($id); // in case it is already started !
		
		$device = $this->ething->get($id);
		
		if($device){
			
			if($device instanceof \Ething\Device\BleaEthernetGateway){
				$gateway = new EthernetGateway($device);
			} else {
				\Log::error("Blea: unable to instanciate the gateway from device {$id}");
			}
			
			if(isset($gateway)){
				\Log::info("Blea: starting gateway '".$device->name()."' id=".$device->id()." type=".$device->type());
				$gateways[$id] = $gateway;
				\PoolStream::add($gateway);
			}
			
		}
		
		
	}
	
	public function stopGateway($id){
		
		$gateway = $this->findGateway($id);
		
		if($gateway){
			\Log::info("Blea: stopping gateway id=".$id);
			unset($gateways[$id]);
			$gateway->close();
			\PoolStream::remove($gateway);
		}
	}
	
	public function findGateway($id){
		return isset($gateways[$id]) ? $gateways[$id] : null;
	}
	
	
	public function createDevice(array $data){
		
		$device = null;
		
		if(isset($data['type'])){
			
			$attr = array(
				'name' => $data['name'],
				'mac' => $data['mac']
			);
			
			switch($data['type']){
				
				case 'miflora':
					$device = \Ething\Device\Miflora::create($attr);
					break;
				
				default:
					$device = \Ething\Device\BleaUnknown::create($attr);
					break;
				
			}
			
		}
		
		return $device;
	}
	
	public function sendData($id, array $data){
		$gateway = $this->findGateway($id);
		
		if($gateway){
			
			$gateway->write($data);
			
		}
	}
	
	public function processData(BleaGateway $gatewayDevice, array $data) {
		
		\Log::debug("Blea: data received from gateway {$gateway->name()} id={$gateway->id()}");
		
		foreach($data as $key => $value){
			
			switch($key){
				
				case 'learn_mode':
					// update the learning state
					$gatewayDevice->learning = boolval($data['learn_mode']);
					break;
				
				case 'id':
					\Log::debug("Blea: device data: ".\json_encode($data));
					
					$device = $this->ething->get($data['id']);
					
					if(!$device){
						// the device is not registered !
						// add it !
						$device = $this->createDevice($data);
					}
					
					if($device){
						// update the device's states
						$device->processData($data, $gatewayDevice);
					}
					
					break;
				
			}
			
		}
		
	}
	
	
	
	
};


