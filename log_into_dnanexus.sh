#!/bin/bash 

###
#Nathaniel Watson
#July 5, 2016
#nathankw@stanford.edu
###

module load dx-toolkit/0.193.0
source $DXTOOLKIT
module load jq/1.5

set -eu -o pipefail

dx_user_conf=dnanexus_conf.json 

function help() {
	echo "Program:"
	echo "  Logs the user into DNAnexus."
	echo -e "\nArgs:"
	echo -e "  -u: Required. Your DNAnexus username, which must appear in $dx_user_conf in order to identify the DNAnexus API token."
	echo -e "      If your username doesn't appear there, add it along with your API key."
}

username=
while getopts "u:h" opt
do
	case $opt in 
		h) help;
			 exit 0
			 ;;
		u) username=$OPTARG
			;;
	esac
done

if [[ -z $username ]]
then
	echo "You must supply a username to the -u argument."
	exit 1
fi

echo $username 

auth_token=$(jq -r ".${username}" $dx_user_conf)

echo $auth_token

dx login --token $auth_token

dx whoami

