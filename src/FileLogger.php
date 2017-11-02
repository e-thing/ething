<?php

namespace Ething;

class FileLogger extends Logger {
	
	protected $file;
	protected $locking = true;
	protected $append = true;
	protected $fp;
	protected $closed = false;
	
	public function __construct(Ething $ething, $name, $file, $level = self::INFO){
		parent::__construct($ething, $name, $level);
		$this->file = $file;
	}
	
	function __destruct(){
		$this->close(); 
    }
	
	protected function write($message, $level){
		
		if($this->closed) return;
		
		// Lazy file open
		if(!isset($this->fp)) {
			if ($this->openFile() === false) {
				return; // Do not write if file open failed.
			}
		}
		
		$message=str_replace("\n"," ",$message).PHP_EOL;
		
		if ($this->locking) {
			$this->writeWithLocking($message);
		} else {
			$this->writeWithoutLocking($message);
		}
	}
	
	protected function openFile() {
		
		$file = $this->file;
		// Create the target folder if needed
		if(!is_file($file)) {
			$dir = dirname($file);
			if(!is_dir($dir)) {
				$success = mkdir($dir, 0777, true);
				if ($success === false) {
					// Failed creating target directory [$dir]. Closing appender.
					$this->close();
					return false;
				}
			}
			@touch($file);
			@chmod($file, 0777);
		}
		
		$mode = $this->append ? 'a' : 'w';
		$this->fp = @fopen($file, $mode);
		if ($this->fp === false) {
			// Failed opening target file. Closing appender.
			$this->fp = null;
			return false;
		}
		
		// Required when appending with concurrent access
		if($this->append) {
			fseek($this->fp, 0, SEEK_END);
		}
		
	}
	
	protected function writeWithLocking($string) {
		if(flock($this->fp, LOCK_EX)) {
			if(fwrite($this->fp, $string) === false) {
				# Failed writing to file. Closing appender.
				$this->close();
			}
			flock($this->fp, LOCK_UN);
		} else {
			# Failed locking file for writing. Closing appender.
			$this->close();
		}
	}
	
	protected function writeWithoutLocking($string) {
		if(fwrite($this->fp, $string) === false) {
			# Failed writing to file. Closing appender.
			$this->close();
		}
	}
	
	public function close() {
		if (is_resource($this->fp)) {
			fclose($this->fp);
		}
		$this->fp = null;
		$this->closed = true;
	}
	
	
	/**
	 * Slightly modified version of http://www.geekality.net/2011/05/28/php-tail-tackling-large-files/
	 * @author Torleif Berger, Lorenzo Stanco
	 * @link http://stackoverflow.com/a/15025877/995958
	 * @license http://creativecommons.org/licenses/by/3.0/
	 */
	public function read($limit = 0){
		
		$adaptive = true;
		$lines = $limit ? $limit : 1;
		
		// Open file
		$f = @fopen($this->file, "rb");
		if ($f === false) return array();
		// Sets buffer size, according to the number of lines to retrieve.
		// This gives a performance boost when reading a few lines from the file.
		if (!$adaptive) $buffer = 4096;
		else $buffer = ($lines < 2 ? 64 : ($lines < 10 ? 512 : 4096));
		// Jump to last character
		fseek($f, -1, SEEK_END);
		// Read it and adjust line number if necessary
		// (Otherwise the result would be wrong if file doesn't end with a blank line)
		if (fread($f, 1) != "\n") $lines -= 1;
		
		// Start reading
		$output = '';
		$chunk = '';
		// While we would like more
		while (ftell($f) > 0 && $lines >= 0) {
			// Figure out how far back we should jump
			$seek = min(ftell($f), $buffer);
			// Do the jump (backwards, relative to where we are)
			fseek($f, -$seek, SEEK_CUR);
			// Read a chunk and prepend it to our output
			$output = ($chunk = fread($f, $seek)) . $output;
			// Jump back to where we started reading
			fseek($f, -mb_strlen($chunk, '8bit'), SEEK_CUR);
			// Decrease our line counter
			$lines -= substr_count($chunk, "\n");
		}
		// While we have too many lines
		// (Because of buffer size we might have read too many)
		while ($lines++ < 0) {
			// Find first newline and remove all text before that
			$output = substr($output, strpos($output, "\n") + 1);
		}
		// Close file and return
		fclose($f);
		
		return array_reverse(explode("\n", trim($output)));
	}
	
	
}

