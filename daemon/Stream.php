<?php


abstract class Stream {
	
	abstract public function getStreams();
	abstract public function process($stream);
	
};
