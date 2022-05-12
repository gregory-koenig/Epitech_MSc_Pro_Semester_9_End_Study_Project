#!/bin/bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )


function createFolder() {
	cd $parent_path
	
	# Look if /build exist and create it if needed.
	if [[ ! -d ./build ]]
	then
		echo -e "/build does not exist on your computer\nCreating the folder in /esp-compiler"
		mkdir ./build
	else
		echo -e "/build already exist"
	fi
}

function compileCFiles() {
	cd $parent_path/runfiles
	
	for f in *.c
	do
		echo "compiling file: $f"
		python3 ../main.py $f --out=${f::-2}
		mv ${f::-2} ../build/
	done
}

function cleanFolders() {
	cd $parent_path/runfiles

	# remove all intermediary files
	rm *.s
	rm *.o
}

createFolder
compileCFiles
cleanFolders
