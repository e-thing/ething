<?php


namespace Ething\Zigate;

use \Ething\Exception;
use \Ething\Zigate\Zigate;

class Message implements \JsonSerializable {
	
	
	protected $type;
	protected $payload;
	protected $rssi;
	
	protected $attr = array();
	
	public static $packetNames = array(
		'8000' => 'Statut',
		'8001' => 'Log message',
		'8002' => 'Data indication',
		'8003' => 'Liste des clusters de l\'objet',
		'8004' => 'Liste des attributs de l\'objet',
		'8005' => 'Liste des commandes de l\'objet',
		'8010' => 'Version list',
		'8024' => 'Network joined / formed',
		'8014' => 'Permit join status response',
		'8006' => 'Non Factory new Restart',
		'8007' => 'Factory New Restart',
		'8030' => 'Bind response',
		'8031' => 'Unbind response',
		'004D' => 'Device announce',
		'8040' => 'Network Address response',
		'8041' => 'IEEE Address response',
		'8042' => 'Node Descriptor response',
		'8043' => 'Simple Descriptor response',
		'8044' => 'Power Descriptor response',
		'8045' => 'ctive Endpoint response',
		'8046' => 'Match Descriptor response',
		'802C' => 'User Descriptor Response',
		'802B' => 'User Descriptor Notify',
		'8034' => 'Complex Descriptor response',
		'8047' => 'Management Leave response',
		'8048' => 'Leave indication',
		'804A' => 'Management Network Update response',
		'804B' => 'System Server Discovery response',
		'804E' => 'Management LQI response',
		'8140' => 'Attribute Discovery response',
		'8028' => 'Authenticate response',
		'8120' => 'Configure Reporting response',
		'8100' => 'Read individual Attribute Response',
		'8110' => 'Write Attribute Response',
		'8102' => 'Report Individual Attribute response',
		'8101' => 'Default response',
		'8029' => 'Out of Band Commissioning Data Response',
		'8060' => 'Add Group response',
		'8061' => 'View Group response',
		'8062' => 'Get Group Membership response',
		'8063' => 'Remove Group response',
		'80A0' => 'View Scene response',
		'80A1' => 'Add Scene response',
		'80A2' => 'Remove Scene response',
		'80A3' => 'Remove All Scene response',
		'80A4' => 'Store Scene response',
		'80A6' => 'Scene Membership response',
		'00D1' => 'Touchlink Status',
		'8401' => 'Zone status change notification',
		'8701' => 'Router Discovery Confirm',
		'8702' => 'APS Data Confirm Fail'
	);
	
	public function __construct($type, $payload = '', $rssi = '00'){
		$this->setType($type);
		$this->setPayload($payload);
		$this->setRssi($rssi);
	}
	
	public function setType($type){
		if(strlen($type) > 4)
			throw new Exception("invalid type");
		$this->type = str_pad($type, 4, "0", STR_PAD_LEFT);
	}
	
	public function getType(){
		return $this->type;
	}
	
	public function setPayload($payload){
		if((strlen($payload) % 2) !== 0)
			throw new Exception("invalid payload length");
		$this->payload = $payload;
		
		$this->decode();
	}
	
	public function getPayload(){
		return $this->payload;
	}
	
	public function setRssi($rssi){
		if(strlen($rssi) > 2)
			throw new Exception("invalid rssi");
		$this->rssi = str_pad($rssi, 2, "0", STR_PAD_LEFT);
	}
	
	public function getRssi(){
		return $this->rssi;
	}
	
	public function getAttributes(){
		return $this->attr;
	}
	
	public __get ( $name ) {
		return isset($this->attr[$name]) ? $this->attr[$name] : null;
	}
	
	public __isset ( $name ) {
		return isset($this->attr[$name]);
	}
	
	public function build(){
		return pack("H*",$this->stringify());
	}
	
	public function computeLength(){
		return strlen($this->payload)/2;
	}
	
	public function computeCRC(){
		$crctmp = 0;
		
		$crctmp= $crctmp ^ hexdec(substr($this->type, 0, 2)) ^ hexdec(substr($this->type, 2, 2));
		
		$len = $this->computeLength();
		$lenhex = str_pad(dechex($len), 4, "0", STR_PAD_LEFT);
		
		$crctmp= $crctmp ^ hexdec(substr($lenhex, 0, 2)) ^ hexdec(substr($lenhex, 2, 2));
		
		$pp = $this->payload . $this->rssi;
		
		for($i=0; $i<$len; $i++){
			$crctmp= $crctmp ^ hexdec($pp[$i*2].$pp[($i*2)+1]);
		}
		
		return $crctmp;
	}
	
	public static function hex2str($hex) {
		$str = '';
		for($i=0;$i<strlen($hex);$i+=2) $str .= chr(hexdec(substr($hex,$i,2)));
		return $str;
	}
	
	public static function transcode($datas) {
		$mess="";
		if (strlen($datas)%2 !=0)
		{
			return $datas;
		}
		for ($i=0;$i<(strlen($datas));$i+=2)
		{
			$byte = $datas[$i].$datas[$i+1];
			
			if ($byte>10)
			{
				 $mess.=$byte;
				
			}else{
				 $mess.="02".sprintf("%02X",(hexdec($byte) ^ 0x10));
			}
		}
		
		return $mess;
	}
	
	public function decode(){
		
		$type = $this->type;
		$payload = $this->payload;
		
		$attr = array();
		
		if( $type=="004d"){  // Device announce
		
			$srcAddr = substr($payload,0,4);
			$ieeeAddr = substr($payload,4,16);
			$macCapability = substr($payload,20,2);
			
			$attr = array(
				'srcAddr' => substr($payload,0,4),
				'ieeeAddr' => substr($payload,4,16),
				'macCapability' => substr($payload,20,2)
			);
			
		} else if( $type=="8000"){  // Status
			// 01 80 00 00 05 95 00 00 00 10 00 03
			/*
			Type: 0x8000 (Status)
			Length: 5
			Status: 0x00 (Success)
			SQN: 0x00
			Message: 
			*/
			$attr = array(
				'status' => substr($payload,0,2),
				'sqn' => substr($payload,2,2),
				'type' => substr($payload,4,4),
				'message' => strlen($payload) > 8 ? Message::hex2str(substr($payload,8)) : ''
			);

		} else if( $type=="8001"){  // Log
			
			$attr = array(
				'logLevel' => hexdec(substr($payload,0,2)),
				'message' => Message::hex2str(substr($payload,2))
			);

		} else if( $type=="8010"){  // Version
			
			$attr = array(
				'appVersion' => hexdec(substr($payload,0,4)),
				'sdkVersion' => hexdec(substr($payload,4,4))
			);

		} else if( $type=="8024"){  // Network joined / formed
			$attr = array(
				'status' => substr($payload,0,2),
				'shortAddr' => substr($payload,2,4),
				'extendedAddr' => substr($payload,6,16),
				'channel' => substr($payload,22,2)
			);
		} else if( $type=="8043"){  // Simple Descriptor Response
			
			$attr = array(
				'sqn' => substr($payload,0,2),
				'status' => substr($payload,2,2),
				'shortAddr' => substr($payload,4,4),
				'length' => hexdec(substr($payload,8,2)),
				'endpoint' => substr($payload,10,2),
				'profile' => substr($payload,12,4),
				'deviceId' => substr($payload,16,4),
				'bitFields' => substr($payload,20,2)
			);
			
			$inClusterCount = substr($payload,22,2);
			$inClusterList = array();
			for($i=0; $i<$inClusterCount; $i++){
				$inClusterList[] = substr($payload,24 + $i*4,4);
			}
			
			$outClusterCount = substr($payload,24 + $inClusterCount*4,2);
			$outClusterList = array();
			for($i=0; $i<$outClusterCount; $i++){
				$outClusterList[] = substr($payload,26 + $inClusterCount*4 + $i*4,4);
			}
			
			$attr['inClusterCount'] = $inClusterCount;
			$attr['inClusterList'] = $inClusterList;
			$attr['outClusterCount'] = $outClusterCount;
			$attr['outClusterList'] = $outClusterList;
			
		} else if( $type=="8045"){  // Active Endpoints Response
			
			$attr = array(
				'sqn' => substr($payload,0,2),
				'status' => substr($payload,2,2),
				'shortAddr' => substr($payload,4,4),
				'endpointCount' => hexdec(substr($payload,8,2)),
				'endpointList' => array()
			);
			
			for ($i = 0; $i < $attr['endpointCount']; $i++)
			{
				$attr['endpointList'][] = substr($payload,(10+$i*2),2);
			}

		} else if( $type=="8101"){  // Default Response
			
			$attr = array(
				'sqn' => substr($payload,0,2),
				'endpoint' => substr($payload,2,2),
				'clusterId' => substr($payload,4,4),
				'commandId' => substr($payload,8,2),
				'statusCode' => substr($payload,10,2)
			);

		} else if( $type=="8102"){  // Report Individual Attribute response
			
			$attr = array(
				'sqn' => substr($payload,0,2),
				'srcAddr' => substr($payload,2,4),
				'endpoint' => substr($payload,6,2),
				'clusterId' => substr($payload,8,4),
				'attrId' => substr($payload,12,4),
				'attrStatus' => substr($payload,16,2),
				'attrType' => substr($payload,18,2),
				'attrSize' => hexdec(substr($payload,20,4)),
				'data' => substr($payload,24)
			);
			
			
			
		} else if( $type=="8401"){  //
			
			$srcAddrMode = substr($payload,8,2);
			
			$d = 4; // depending on srcAddrMode, 4 or 8
			
			$attr = array(
				'sqn' => substr($payload,0,2),
				'endpoint' => substr($payload,2,2),
				'clusterId' => substr($payload,4,4),
				'srcAddrMode' => $srcAddrMode,
				'srcAddr' => substr($payload,10,$d),
				'zoneStatus' => substr($payload,10 + $d,4),
				'extendedStatus' => substr($payload,14 + $d,2),
				'zoneId' => substr($payload,16 + $d,2)
			);

		} else if( $type=="8702"){  // APS Data Confirm Fail
			
			$dstAddrMode = substr($payload,6,2);
			
			$d = strlen($payload) - 10; // depending on dstAddrMode
			
			$attr = array(
				'status' => substr($payload,0,2),
				'srcEndpoint' => substr($payload,2,2),
				'dstEndpoint' => substr($payload,4,2),
				'dstAddrMode' => $dstAddrMode,
				'dstAddr' => substr($payload,8,$d),
				'sqn' => substr($payload,8+$d,2)
			);			
			

		}
		
		$this->attr = $attr;
		
	}
	
	// packet must be an hexadecimal string
	// 01 80 00 00 05 95 00 00 00 10 00 03
	static public function parse($packet){

		if(strlen($packet)<14){
			throw new Exception("invalid packet len<7 [{$packet}]");
		}

		if(substr($packet, 0, 2) !== '01'){
			throw new Exception("packet does not start with 0x01 [{$packet}]");
		}

		if(substr($packet, -2) !== '03'){
			throw new Exception("packet does not end with 0x03 [{$packet}]");
		}


		$datas = substr($packet, 2, -2);
		
		$crctmp = 0;
		
		//message type
		$type=$datas[0].$datas[1].$datas[2].$datas[3];
		$crctmp= $crctmp ^ hexdec($datas[0].$datas[1]) ^ hexdec($datas[2].$datas[3]);
		
		//message length
		$ln=hexdec($datas[4].$datas[5].$datas[6].$datas[7]);
		$crctmp= $crctmp ^ hexdec($datas[4].$datas[5]) ^ hexdec($datas[6].$datas[7]);

		if(strlen($datas) !== (5+$ln)*2){
			throw new Exception("invalid packet length mismatch [{$packet}]");
		}

		//CRC
		$crc=hexdec($datas[8].$datas[9]);

		//payload
		$payload="";
		for($i=0;$i<$ln;$i++)
		{
			$payload.=$datas[10+($i*2)].$datas[10+(($i*2)+1)];
			$crctmp= $crctmp ^ hexdec($datas[10+($i*2)].$datas[10+(($i*2)+1)]);
		}

		$rssi = strlen($payload)>1 ? substr($payload, -2) : '00';
		$payload = substr($payload, 0, -2);
		
		if($crctmp !== $crc){
			throw new Exception("invalid packet CRC mismatch [{$packet}]");
		}
		
		return new Message($type, $payload, $rssi);

	}
	
	public function stringify(){
		$msg = '01';
		
		$msg .= self::transcode($this->type);
		
		$msg .= self::transcode(str_pad(dechex($this->computeLength()), 4, "0", STR_PAD_LEFT));
		
		$msg .= str_pad(dechex($this->computeCRC()), 2, "0", STR_PAD_LEFT);
		
		$msg .= self::transcode($this->payload);
        
        $msg .= '03';
		
		return $msg;
	}
	
	public function jsonSerialize() {
		return array(
			'type' => $this->type,
			'rssi' => $this->rssi,
			'payload' => $this->payload,
			'attr' => $this->attr
		);
	}
	
	static public function decodeMacCapability($macCapability){
		if(is_string($macCapability)) $macCapability = hexdec(substr($macCapability, 0, 2));
		
		return array(
			'Alternate PAN Coordinator' =>  boolval($macCapability & 0b00000001),
			'Device Type' =>  boolval($macCapability & 0b00000010) ? 'FFD' : 'RFD',
			'Power Source' =>  boolval($macCapability & 0b00000100) ? 'main' : 'battery',
			'Receiver On When Idle' =>  boolval($macCapability & 0b00001000),
			'Security Capability' =>  boolval($macCapability & 0b01000000),
			'Allocate Address' =>  boolval($macCapability & 0b10000000)
		);
	}
	
	public function toHumanReadable(){
		
		$name = isset(Message::$packetNames[$this->type]) ? Message::$packetNames[$this->type] : '?';
		
		$attrstr = '';
		foreach($this->attr as $key => $value){
			$attrstr .= ' '.$key.': ';
			if(is_array($value)){
				
				if($key === "inClusterList" || $key === "outClusterList"){
					foreach($value as $i => &$clusterId){
						$clusterId .= ' ('.Zigate::clusterIdToName($clusterId).')';
					}
				}
				
				$attrstr .= implode(';',$value);
				
			} else {
				$attrstr .= (string)$value;
				
				if($key === "clusterId"){
					$attrstr .= ' ('.Zigate::clusterIdToName($value).')';
				}
			}
			
			
		}
		
		if(!empty($attrstr)) $attrstr = ' ,'.$attrstr;
		
		return "type: 0x{$this->type} ({$name}) , payload: {$this->payload} , rssi: 0x{$this->rssi}".$attrstr;
	}
	
	public function __toString(){
		return $this->stringify();
	}
	
	
};


