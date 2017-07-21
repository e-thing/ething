#!/bin/bash

ROOT_DIR=$(dirname "$(readlink -f "$0")")

cd ${ROOT_DIR}

function compiljs {
   
   out=$1
   shift
   
   echo "compiling ${out} ..."
   
   > ${out}
   
	while (($#)); do
		
		echo "adding $1 ..."
		
		if [ -e "$1" ] ; then
			echo "/* @file: $1 */" >> ${out}
			cat "$1" >> ${out}
		else
			echo "file not found $1"
		fi
		shift
	done
	
	# minify
	#if [ -s ${out} ] ; then
	#	echo "minifying ${out} ..."
	#	
	#	curl -s \
	#	  -d compilation_level=SIMPLE_OPTIMIZATIONS \
	#	  -d output_format=text \
	#	  -d output_info=compiled_code \
	#	 --data-urlencode "js_code@${out}" \
	#	 http://closure-compiler.appspot.com/compile \
	#	  > ${out%%.*}.min.js
	#fi
   
}

function compilcss {
   
   out=$1
   shift
   
   echo "compiling ${out} ..."
   
   > ${out}
   
	while (($#)); do
		
		echo "adding $1 ..."
		
		if [ -e "$1" ] ; then
			echo "/* @file: $1 */" >> ${out}
			cat "$1" >> ${out}
		else
			echo "file not found $1"
		fi
		shift
	done
   
   # minify
	#if [ -s ${out} ] ; then
	#	echo "minifying ${out} ..."
	#	
	#	curl -s \
	#	 --data-urlencode "input@${out}" \
	#	 http://cssminifier.com/raw \
	#	  > ${out%%.*}.min.css
	#fi
	
}


compiljs "core.js" "src/utils.js" "src/node.js" "src/event.js" "src/deferred.js" "src/api.js" "src/arbo.js" "src/rules.js"



