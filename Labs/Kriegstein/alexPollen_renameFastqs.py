
import os
import re
import subprocess
from argparse import ArgumentParser

whiteSpaceReg = re.compile(r'\s')

def runSanityChecks(origName,newName):
	"""
	Function : Perform a few sanity checks, such as the new file name without the added prefix is equal to the orig file name."
	Args     : origName - The original file name.
						 newName - The new file name.
	"""
	#check 1
	newNameWithoutAddedPrefix =  newName.lsplit("_",1)[1]
	if newNameWithoutAddedPrefix != origName:
		raise Exception("Failed Sanity check 1 - The new file name '{newName}' minus the added prefix '{newNameWithoutAddedPrefix}' does not match the orig filename '{origName}' !".format(newName=newName,newNameWithoutAddedPrefix=newNameWithoutAddedPrefix,origName=origName))

def validateFileName(filename):
	"""
	Function : Makes sure the input filename doens't contain any whitespace or '/' characters.
	"""
	if whiteSpaceReg.search(filename):
		raise Exception("Filename '{filename}' contains whitespace. This script doesn't support whitespace in file names.".format(filename=filename))
	if "/" in filename:
		raise Exception("Filename '{filename}' contains a '/' character, which is not supported by this script.".format(filename=filename))	


description = "Renames FASTQ files based on the original and new name pairings found in the tab-delimited input file. The names should not contain paths."
parser = ArgumentParser(description=description)
parser.add_argument('-i','--infile',required=True,help="The input tab-delimited file. Must contain a column for the original file name and another for the new file name, where each row forms an orig name and new name pair. The file names should not include paths.")
parser.add_argument('-a','--original-name-column',type=int,required=True,help="The 1-base index of the column position that contains the FASTQ files names as output by the SCGPM pipeline (raw file names).")
parser.add_argument('-b','--new-name-column',type=int,required=True,help="The 1-base index of the column that contains the new FASTQ file names.")
parser.add_argument('-s','--base-search-dir',required=True,help="The starting directory in which to search for the file names in --infile designated by column position --original-name-column.")
parser.add_argument('--header',action="store_true",help="Presence of this option indicates that there is a header line as the first line in --infile, and should be ignored.")
parser.add_argument('--sanity-check',action="store_true",help="Presence of this option indicates to perform a few sanity checks, such as the new file name without the added prefix is equal to the orig file name.")

args = parser.parse_args()
infile = args.infile
origNameCol = args.original_name_column -1
newNameCol  = args.new_name_column -1
startingDir = args.base_search_dir
header = args.header
sanityCheck = args.sanity_check

lineNum = 0
names = {}
fh = open(infile)
if header:
	fh.readline()
	lineNum += 1
for line in fh:
	lineNum += 1
	line = line.strip()
	if not line:
		continue
	line = line.split("\t")
	origName = line[origNameCol].strip()
	newName = line[newNameCol].strip()
	if not origName:
		raise Exception("No file name found in column position {col} on line number {lineNum}.".format(col=origNameCol + 1,lineNum=lineNum))
	if not newName:
		raise Exception("No file name found in column position {col} on line number {lineNum}.".format(col=newNameCol + 1,lineNum=lineNum))
	validateFileName(origName)
	validateFileName(newName)
	if origName not in names:
		names[origName] = ""
	else:
		raise Exception("File name '{origName}' in column position {col} exists multiple times!".format(col=origNameCol + 1))	
	if newName in names.values():
		raise Exception("File name '{newName}' in column position {col} exists multiple times!".format(col=newNameCol + 1))
	names[origName] = newName
	if sanityCheck:
		runSanityChecks(origName,newName)

#now see if I can find each occurrence of origName 


os.chdir(startingDir)
for origName in names:
	cmd = "find . -name {origName} -print".format(origName=origName)
	popen = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE) #checkRetcode=False b/c the 'find' cmd doesn't error if it doens't find anything.
	stdout,stderr = popen.communicate()
	stdout = stdout.strip()
	stderr = stderr.strip()
	retcode = popen.returncode
	if retcode:
		print("Command '{cmd}' failed with return code '{retcode}'. \n\nSTDOUT was '{stdout}'. \n\nSTDERR was '{stderr}'".format(cmd=cmd,retcode=retcode,stdout=stdout,stderr=stderr))
	if not stdout:
		Exception("Can't find file '{origName}' in order to rename it.")
	print("Renaming '{stdout}' to '{newName}'".format(stdout=stdout,newName=names[origName]))
	os.rename(stdout,names[origName])
