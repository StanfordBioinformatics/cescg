#!/bin/bash -eu 
set -o pipefail

###
#Nathaniel Watson
#2016-11-17
###

###CONFIG###
dx_user_name=nathankw
output_dir=/data/cirm/submit/stanford/Labs
logfile=/data/cirm/submit/stanford/software/scgpm_seqresults_dnanexus/scripts/log_2016-11-16.txt
###########

function help {
  echo "howdy"
}

dx_proj_id=
infile= 

help() {
	echo "Wrapper for download_project.py in the git@github.com:StanfordBioinformatics/scgpm_seqresults_dnanexus.git repository."
	echo "In the CONFIG section near the top of this script, enter values for the variables dx_user_name, output_dir, and logfile."
	echo "This wrapper is thus useful for standardizing the values of the aforementioned variables, for standardized worfklows."
	echo "This wrapper also sets the scHub=True project property in DNAnexus after a give project is successfully downloaded."
	echo
	echo "Args"
	echo " -f File name containing DNAnexus project IDs, one per line."
	echo " -i str. A DNAnexus project ID."
}

while getopts "i:f:h" opt
do
  case $opt in  
    f) infile=${OPTARG}
       ;;  
		i) dx_proj_id=${OPTARG}
			 ;;
    h) help
       exit
       ;;  
  esac
done

if [[ ${#@} -eq 0 ]]
then
  help
fi

dx_proj_ids=()

if [[ -n $dx_proj_id ]]
then
	dx_proj_ids+=(${dx_proj_id})
else
	while read dx_proj_id
	do
		if [[ ${dx_proj_id} =~ ^# ]]
		then
			continue
		fi
		dx_proj_ids+=($dx_proj_id)
	done < ${infile}
fi

#echo ${dx_proj_ids[@]}


for i in ${dx_proj_ids[@]}
do
	lab=$(dx describe ${dx_proj_id} --verbose --json | jq -r .properties.lab)

	lab_dir=${output_dir}/${lab}	
	if [[ ! -d ${lab_dir} ]]
	then
		mkdir ${lab_dir}
	fi

	download_project.py -u ${dx_user_name} --download-dir ${lab_dir} --dx-project-id ${dx_proj_id} -l ${logfile}
	if [[ $? -ne 0 ]]
	then
		echo "Failed to download project ${dx_proj_id}."
		exit
	fi
	add_props_to_project.py --dx-project-id=${dx_proj_id} scHub=True
	if [[ $? -ne 0 ]]
	then
		echo "Failed to add the scHub:True property to ${dx_proj_id}."
		exit
	fi
done 
