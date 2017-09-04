<?php

namespace Ething;


// gridfs helpers

class DbFs
{
    
	private $ething;
	
	public function __construct(Ething $ething){
		
		$this->ething = $ething;
		
	}
	
	public function storeFile($filename, $contents, $metadata = array()){
		if(!empty($contents)){
			$bucket = $this->ething->db()->selectGridFSBucket();
			
			$stream = $bucket->openUploadStream($filename, array(
				'metadata' => $metadata
			));
			
			fwrite($stream, $contents);
			$id = (string)$bucket->getFileIdForStream($stream);
			fclose($stream);
			
			return $id;
		}
		
		return null;
	}
	
	public function retrieveFile($id){
		if(isset($id)){
			$bucket = $this->ething->db()->selectGridFSBucket();
			try {
				$stream = $bucket->openDownloadStream(new \MongoDB\BSON\ObjectId($id));
				return stream_get_contents($stream);
			} catch(\MongoDB\GridFS\Exception\FileNotFoundException $e){}
		}
		
		return null;
	}
	
	public function removeFile($id){
		if(isset($id)){
			$bucket = $this->ething->db()->selectGridFSBucket();
			try {
				$bucket->delete(new \MongoDB\BSON\ObjectId($id));
			} catch(\MongoDB\GridFS\Exception\FileNotFoundException $e){}
		}
	}
	
	public function getFileMetadata($id){
		$metadata = array();
		
		if(isset($id)){
			$bucket = $this->ething->db()->selectGridFSBucket();
			try {
				$stream = $bucket->openDownloadStream(new \MongoDB\BSON\ObjectId($id));
				$metadata = $bucket->getFileDocumentForStream($stream);
			} catch(\MongoDB\GridFS\Exception\FileNotFoundException $e){}
		}
		
		return $metadata;
	}
	
	public function getFileSize($id){
		if(isset($id)){
			$bucket = $this->ething->db()->selectGridFSBucket();
			try {
				$stream = $bucket->openDownloadStream(new \MongoDB\BSON\ObjectId($id));
				$metadata = $bucket->getFileDocumentForStream($stream);
				return $metadata['length'];
			} catch(\MongoDB\GridFS\Exception\FileNotFoundException $e){}
		}
		
		return 0;
	}
	
}

