<?php
	

	/**
	 * @swagger-definition
	 * "File":{ 
	 *   "type": "object",
	 *   "description": "File resource representation",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Resource"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "expireAfter": {
	 * 		          "type":"number",
	 * 		          "description":"The amount of time (in seconds) after which this resource will be removed."
	 * 		       },
	 *             "size": {
	 * 		          "type":"number",
	 * 		          "description":"The size of this resource in bytes",
	 *                "readOnly": true
	 * 		       },
	 *             "hasThumbnail": {
	 * 		          "type":"boolean",
	 * 		          "description":"True if this file has a thumbnail. Thumbnail is only available for file with MIME type __image/*__). See the /file/<id>/thumbnail endpoint for more details.",
	 *                "readOnly": true
	 * 		       },
	 *             "isText": {
	 * 		          "type":"boolean",
	 * 		          "description":"True if this file has text based content.",
	 *                "readOnly": true
	 * 		       },
	 * 		       "mime":{  
	 * 		          "type":"string",
	 * 		          "description":"The MIME type of the file (automatically detected from the content).",
	 *                "readOnly": true
	 * 		       }
	 * 		   }
	 * 		}
	 *   ]
	 * }
	 */

namespace Ething;


class File extends Resource
{
	public static $defaultAttr = [
		'expireAfter' => null
	];
	
	
	public function jsonSerialize() {
		$o = parent::jsonSerialize();
		$o['hasThumbnail'] = $this->hasAttr('_thumb');
		return $o;
	}
	
	
	public function remove() {
		
		// remove the file from GridFS
		$this->ething->fs->removeFile($this->getAttr('_data'));
		
		// remove any thumbnail
		$this->ething->fs->removeFile($this->getAttr('_thumb'));
		
		// remove the resource
		parent::remove();
		
	}
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			case 'name':
				if($ret = parent::validate($key,$value,$context)){
					$context['callbacks'][] = function($r) {
						$r->updateMeta(static::META_MIME|static::META_TEXT);
					};
				}
				break;
			case 'expireAfter':
				if($value===0) $value=null;
				$ret = is_null($value) || (is_int($value) && $value>0);
				break;
			case 'content':
				if(is_string($value) || is_null($value)){
					
					$content = base64_decode($value);
					if($content===false)
						throw new Exception('invalid base64 data for the field "content"');
					
					$context['callbacks'][] = function($r) use ($content) {
						$r->write($content);
					};
					
					$ret = true;
				}
				unset($context['config'][$key]);// remove this key
				break;
			default:
				$ret = parent::validate($key,$value,$context);
				break;
		}
		return $ret;
	}
	
	// is called regularly
	public function checkExpiredData() {
		// remove the file if the data has expired
		if( $this->isExpired() ){
			$this->remove();
		}
	}
	
	public function isExpired() {
		return $this->expireAfter && ($this->modifiedDate + $this->expireAfter < time());
	}
	
	
	
	public function read() {
		$contents = $this->ething->fs->retrieveFile($this->getAttr('_data'));
		return isset($contents) ? $contents : '';
	}
	
	public function write($bytes) {
		
		// remove that file if it exists
		$this->ething->fs->removeFile($this->getAttr('_data'));
		$this->removeAttr('_data');
		$this->setAttr('size', 0);
		
		if(!empty($bytes)){
			$this->setAttr('_data', $this->ething->fs->storeFile('File/'.$this->id().'/content', $bytes, array(
				'parent' => $this->id()
			)));
			$this->setAttr('size', $this->ething->fs->getFileSize($this->getAttr('_data')));
		}
		
		$this->updateMeta(static::META_ALL, $bytes);
		
		$this->update();
		
		// generate an event
		$this->dispatchSignal(Event\FileDataModified::emit($this));
		
		return true;
	}
	
	public function append($bytes) {
		$d = $this->read();
		$d .= $bytes;
		return $this->write($d);
	}
	
	
	// create a new resource
	public static function create(Ething $ething, array $attributes, Resource $createdBy = null) {
		return parent::createRessource( 
			$ething,
			array_merge(self::$defaultAttr, $attributes),
			array(
				'size' => 0,
				'isText' => true, // will be updated through the 'name' validator callback !
				'mime' => '' // will be updated through the 'name' validator callback !
			),
			$createdBy
		);
	}
	
	
	// update meta information : mimeType, isText and thumbnail
	const META_MIME = 1;
	const META_TEXT = 2;
	const META_THUMB = 4;
	const META_ALL = 255;
	const META_NONE = 0;
	// the content can be provided to avoid reading it from the database
	public function updateMeta($opt = self::META_ALL, $content = null) {
		
		
		if($opt & self::META_MIME){
			/* try to find the correct mime type according to the extension first, then if not found, by the content */
			
			$ext = pathinfo($this->name(), PATHINFO_EXTENSION);
			if(isset(self::$extToMime[$ext]))
				$mime =  self::$extToMime[$ext];
			
			if(!isset($mime)){
				// try to get the mime type from the content
				if(!isset($content))
					$content = $this->read();
				$finfo = new \finfo(FILEINFO_MIME_TYPE);
				$mime = $finfo->buffer($content);
			}
			
			$this->setAttr('mime',$mime);
			
		}
		
		if($opt & self::META_TEXT){
			
			$mime = $this->mime;
			if(preg_match('/^text\//i',$mime))
				$isText = true;
			else if(preg_match('/^(image|audio|video)\//i',$mime))
				$isText = false;
			// other mime type are undetermined
			
			if(!isset($isText)){
				if(!isset($content))
					$content = $this->read();
				
				$isText = static::isPrintable($content);
			}
			
			$this->setAttr('isText',$isText);
			
		}
		
		if($opt & self::META_THUMB){
			
			if(!isset($content))
				$content = $this->read();
		
			$thumb = (!empty($content) && preg_match('/^image\//i',$this->mime) && extension_loaded('gd')) ? self::createThumb($content,128) : null;
			
			$this->ething->fs->removeFile($this->getAttr('_thumb'));
			$this->removeAttr('_thumb');
			
			if(!empty($thumb))
				$this->setAttr('_thumb', $this->ething->fs->storeFile('App/'.$this->id().'/thumb', $thumb, array(
					'parent' => $this->id()
				)));
			
		}
		
		$this->update(false);
		
	}
	
	
	
	private static $extToMime = array(
	  "hqx" => "application/mac-binhex40", 
	  "cpt" => "application/mac-compactpro", 
	  "doc" => "application/msword", 
	  "bin" => "application/octet-stream", 
	  "dms" => "application/octet-stream", 
	  "lha" => "application/octet-stream", 
	  "lzh" => "application/octet-stream", 
	  "exe" => "application/octet-stream", 
	  "class" => "application/octet-stream", 
	  "so" => "application/octet-stream", 
	  "dll" => "application/octet-stream", 
	  "oda" => "application/oda", 
	  "pdf" => "application/pdf", 
	  "ai" => "application/postscript", 
	  "eps" => "application/postscript", 
	  "ps" => "application/postscript", 
	  "smi" => "application/smil", 
	  "smil" => "application/smil", 
	  "wbxml" => "application/vnd.wap.wbxml", 
	  "wmlc" => "application/vnd.wap.wmlc", 
	  "wmlsc" => "application/vnd.wap.wmlscriptc", 
	  "bcpio" => "application/x-bcpio", 
	  "vcd" => "application/x-cdlink", 
	  "pgn" => "application/x-chess-pgn", 
	  "cpio" => "application/x-cpio", 
	  "csh" => "application/x-csh", 
	  "dcr" => "application/x-director", 
	  "dir" => "application/x-director", 
	  "dxr" => "application/x-director", 
	  "dvi" => "application/x-dvi", 
	  "spl" => "application/x-futuresplash", 
	  "gtar" => "application/x-gtar", 
	  "hdf" => "application/x-hdf", 
	  "js" => "application/javascript",
	  "json" => "application/json", 
	  "skp" => "application/x-koan", 
	  "skd" => "application/x-koan", 
	  "skt" => "application/x-koan", 
	  "skm" => "application/x-koan", 
	  "latex" => "application/x-latex", 
	  "nc" => "application/x-netcdf", 
	  "cdf" => "application/x-netcdf", 
	  "sh" => "application/x-sh", 
	  "shar" => "application/x-shar", 
	  "swf" => "application/x-shockwave-flash", 
	  "sit" => "application/x-stuffit", 
	  "sv4cpio" => "application/x-sv4cpio", 
	  "sv4crc" => "application/x-sv4crc", 
	  "tar" => "application/x-tar", 
	  "tcl" => "application/x-tcl", 
	  "tex" => "application/x-tex", 
	  "texinfo" => "application/x-texinfo", 
	  "texi" => "application/x-texinfo", 
	  "t" => "application/x-troff", 
	  "tr" => "application/x-troff", 
	  "roff" => "application/x-troff", 
	  "man" => "application/x-troff-man", 
	  "me" => "application/x-troff-me", 
	  "ms" => "application/x-troff-ms", 
	  "ustar" => "application/x-ustar", 
	  "src" => "application/x-wais-source", 
	  "xhtml" => "application/xhtml+xml", 
	  "xht" => "application/xhtml+xml", 
	  "zip" => "application/zip", 
	  "au" => "audio/basic", 
	  "snd" => "audio/basic", 
	  "mid" => "audio/midi", 
	  "midi" => "audio/midi", 
	  "kar" => "audio/midi", 
	  "mpga" => "audio/mpeg", 
	  "mp2" => "audio/mpeg", 
	  "mp3" => "audio/mpeg", 
	  "aif" => "audio/x-aiff", 
	  "aiff" => "audio/x-aiff", 
	  "aifc" => "audio/x-aiff", 
	  "m3u" => "audio/x-mpegurl", 
	  "ram" => "audio/x-pn-realaudio", 
	  "rm" => "audio/x-pn-realaudio", 
	  "rpm" => "audio/x-pn-realaudio-plugin", 
	  "ra" => "audio/x-realaudio", 
	  "wav" => "audio/x-wav", 
	  "pdb" => "chemical/x-pdb", 
	  "xyz" => "chemical/x-xyz", 
	  "bmp" => "image/bmp", 
	  "gif" => "image/gif", 
	  "ief" => "image/ief", 
	  "jpeg" => "image/jpeg", 
	  "jpg" => "image/jpeg", 
	  "jpe" => "image/jpeg", 
	  "png" => "image/png", 
	  "tiff" => "image/tiff", 
	  "tif" => "image/tif", 
	  "djvu" => "image/vnd.djvu", 
	  "djv" => "image/vnd.djvu", 
	  "wbmp" => "image/vnd.wap.wbmp", 
	  "ras" => "image/x-cmu-raster", 
	  "pnm" => "image/x-portable-anymap", 
	  "pbm" => "image/x-portable-bitmap", 
	  "pgm" => "image/x-portable-graymap", 
	  "ppm" => "image/x-portable-pixmap", 
	  "rgb" => "image/x-rgb", 
	  "xbm" => "image/x-xbitmap", 
	  "xpm" => "image/x-xpixmap", 
	  "xwd" => "image/x-windowdump", 
	  "igs" => "model/iges", 
	  "iges" => "model/iges", 
	  "msh" => "model/mesh", 
	  "mesh" => "model/mesh", 
	  "silo" => "model/mesh", 
	  "wrl" => "model/vrml", 
	  "vrml" => "model/vrml", 
	  "css" => "text/css", 
	  "html" => "text/html", 
	  "htm" => "text/html", 
	  "asc" => "text/plain", 
	  "txt" => "text/plain", 
	  "rtx" => "text/richtext", 
	  "rtf" => "text/rtf", 
	  "sgml" => "text/sgml", 
	  "sgm" => "text/sgml", 
	  "tsv" => "text/tab-seperated-values", 
	  "wml" => "text/vnd.wap.wml", 
	  "wmls" => "text/vnd.wap.wmlscript", 
	  "etx" => "text/x-setext", 
	  "xml" => "text/xml", 
	  "xsl" => "text/xml", 
	  "mpeg" => "video/mpeg", 
	  "mpg" => "video/mpeg", 
	  "mpe" => "video/mpeg", 
	  "qt" => "video/quicktime", 
	  "mov" => "video/quicktime", 
	  "mxu" => "video/vnd.mpegurl", 
	  "avi" => "video/x-msvideo", 
	  "movie" => "video/x-sgi-movie"
	);
	
	public static function isPrintable($content, $limit = 1000){
		
		$l = min($limit,strlen($content));
		
		for($i=0; $i<$l; $i++){
			$code = ord($content[$i]);
			
			if(($code<32 || $code>126) && $code!=9 && $code!=10 && $code!=13 && ($code<128 || $code>254))
				return false;
		}
		
		return true;
	}
	
	
	
	public function readThumbnail() {
		return $this->ething->fs->retrieveFile($this->getAttr('_thumb'));
	}
	
	public static function createThumb( $imagedata, $thumbWidth ) 
	{
		  $thumbdata = null;
		  // load image and get image size
		  $img = @imagecreatefromstring( $imagedata );
		  if($img){ // else unknown format
			$width = imagesx( $img );
			$height = imagesy( $img );

			// calculate size
			$ratio = (($width / $height) < 1) ?
				$thumbWidth / $width : $thumbWidth / $height;
			$x = max(0, round($width / 2 - ($thumbWidth / 2) / $ratio));
			$y = max(0, round($height / 2 - ($thumbWidth / 2) / $ratio));

			// create a new temporary image
			$tmp_img = imagecreatetruecolor( $thumbWidth, $thumbWidth );
			imagealphablending( $tmp_img, false );
			imagesavealpha( $tmp_img, true );

			// copy and resize old image into new image 
			if(imagecopyresized( $tmp_img, $img, 0, 0, $x, $y, $thumbWidth, $thumbWidth, round($thumbWidth / $ratio, 0), round($thumbWidth / $ratio) )){

				// save thumbnail into a string
				ob_start();
				imagepng($tmp_img);
				$thumbdata = ob_get_contents(); // read from buffer
				ob_end_clean(); // delete buffer
			}
			
			imagedestroy($tmp_img);
			imagedestroy($img);
		}
		
		return $thumbdata;
	}
	
}

