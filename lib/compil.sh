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


compiljs "core.js" "src/core/utils.js" "src/core/deferred.js" "src/core/api.js" "src/core/arbo.js" "src/core/swagger.js"

compiljs "ui.js" "src/ui/utils.js" "src/ui/form.js" "src/ui/modal.js" "src/ui/table.js" "src/ui/browser.js" "src/ui/opendialog.js" "src/ui/savedialog.js" "src/ui/textviewer.js" "src/ui/tableviewer.js" "src/ui/mapviewer.js" "src/ui/imageviewer.js" "src/ui/graph.js" "src/ui/deviceviewer.js" "src/ui/formmodal.js"

compilcss "ui.css" "src/ui/table.css" "src/ui/browser.css" "src/ui/modal.css" "src/ui/form.css" "src/ui/common.css" "src/ui/textviewer.css" "src/ui/tableviewer.css" "src/ui/mapviewer.css" "src/ui/imageviewer.css" "src/ui/graph.css" "src/ui/deviceviewer.css"


