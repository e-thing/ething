<?php

namespace Ething;

class RollingFileLogger extends FileLogger {
	
	protected $maxFileSize = 10485760;
	protected $maxBackupIndex = 1;
	protected $compress = false; // Requires the zlib extension
	
	const COMPRESS_CHUNK_SIZE = 102400; // 100KB
	
	
	
	protected function write($message, $level) {
		
		// Lazy file open
		if(!isset($this->fp)) {
			if ($this->openFile() === false) {
				return; // Do not write if file open failed.
			}
		}
		
		$message=str_replace("\n"," ",$message).PHP_EOL;
		
		// Lock the file while writing and possible rolling over
		if(flock($this->fp, LOCK_EX)) {
			
			// Write to locked file
			if(fwrite($this->fp, $message) === false) {
				# Failed writing to file. Closing appender.
				$this->close();
			}
			
			// Stats cache must be cleared, otherwise filesize() returns cached results
			// If supported (PHP 5.3+), clear only the state cache for the target file
			clearstatcache(true, $this->file);
			
			// Rollover if needed
			if (filesize($this->file) > $this->maxFileSize) {
				try {
					$this->rollOver();
				} catch (LoggerException $ex) {
					# Rollover failed: " . $ex->getMessage() . " Closing appender.
					$this->close();
				}
			}
			
			flock($this->fp, LOCK_UN);
		} else {
			# Failed locking file for writing. Closing appender.
			$this->close();
		}
	}
	
	private function rollOver() {
		// If maxBackups <= 0, then there is no file renaming to be done.
		if($this->maxBackupIndex > 0) {
			// Delete the oldest file, to keep Windows happy.
			$file = $this->file . '.' . $this->maxBackupIndex;
			
			if (file_exists($file) && !unlink($file)) {
				throw new LoggerException("Unable to delete oldest backup file from [$file].");
			}
			// Map {(maxBackupIndex - 1), ..., 2, 1} to {maxBackupIndex, ..., 3, 2}
			$this->renameArchievedLogs($this->file);
	
			// Backup the active file
			$this->moveToBackup($this->file);
		}
		
		// Truncate the active file
		\ftruncate($this->fp, 0);
		\rewind($this->fp);
	}
	
	private function moveToBackup($source) {
		if ($this->compress) {
			$target = $source . '.1.gz';
			$this->compressFile($source, $target);
		} else {
			$target = $source . '.1';
			\copy($source, $target);
		}
	}
	
	private function compressFile($source, $target) {
		$target = 'compress.zlib://' . $target;
		
		$fin = fopen($source, 'rb');
		if ($fin === false) {
			throw new LoggerException("Unable to open file for reading: [$source].");
		}
		
		$fout = fopen($target, 'wb');
		if ($fout === false) {
			throw new LoggerException("Unable to open file for writing: [$target].");
		}
	
		while (!feof($fin)) {
			$chunk = fread($fin, self::COMPRESS_CHUNK_SIZE);
			if (false === fwrite($fout, $chunk)) {
				throw new LoggerException("Failed writing to compressed file.");
			}
		}
	
		fclose($fin);
		fclose($fout);
	}
	
	private function renameArchievedLogs($fileName) {
		for($i = $this->maxBackupIndex - 1; $i >= 1; $i--) {
			
			$source = $fileName . "." . $i;
			if ($this->compress) {
				$source .= '.gz';
			}
			
			if(file_exists($source)) {
				$target = $fileName . '.' . ($i + 1);
				if ($this->compress) {
					$target .= '.gz';
				}				
				
				\rename($source, $target);
			}
		}
	}
	
}

