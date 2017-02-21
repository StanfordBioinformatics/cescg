#!/bin/env python
# -*- coding: utf-8 -*-

python run_encode_rnaseq.py -s project-F0b1P4Q04fx48f2yk1j3gG61 project-F0bJ3Xj03jJF87gf94X2fv8F -w	project-F2YpBxQ0721Fjp343Q7bQKXx -b /srv/gsfs0/software/gbsc/cescg/Labs/Loring/barcodes.txt

import argparse 
import pdb

import dxpy

from scgpm_seqresults_dnanexus import dnanexus_utils as du #module load gbsc/scgmp_seqresults_dnanexus/current

HG19 = "hg19"
HG38 = "hg38"
NATHANKW_RESOURCES_PROJ= "project-BxxYqbQ0v3VQz5z2bvFyF6YV"

description = ""
parser = argparse.ArgumentParser(description=description,formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-g","--genome",required=True,choices=(HG19,HG38),help="The reference genome to use in the analysis.")
parser.add_argument("-w","--working-dx-proj",required=True,help="The ID of the DNAnexus project in which to run the ENCODE Long RNA-Seq workflow. You must have previously copied the workflow into this project in the root folder.")
parser.add_argument("-s","--sequencing_projects",required=True,narg="+",help="The DNAnexus projects that contain the sequencing results.")
parser.add_argument("-b","--barcodes-file",required=True,help="Text file containing one or more barcodes (one per line).")
parser.add_argument("-t","--technical-replicates",required=True,type=int,help="The number of technical replicates for each sample (barcode). Each technical replicate should have the same barcode since it was sequenced multiple times - either on multiple lanes of the same flowcell, or different lanes of different flowcells, or both. This information is used to perform a check before running the workflow. The check asserts the following for each sample:
	#forward_read_fiels == #num_reverse_read_files == #technical_replicates
")

args = parser.parse_args()
genome = args.genome
working_proj = args.working_dx_proj
sequencing_projects = args.sequencing_projects
barcodes_file = args.barcodes_file
num_tech_reps = args.technical_replicates

bfh = open(barcodes_file)
barcodes = []
for line in bfh:
	line = line.strip()
	if not line:
		continue
	barcodes.append(line)

#When copying the ENCODE Long RNA-Seq workflow into a DNAnexus projects, in addition to copying the workflow object, the copy action also copies over the STAR and RSEM tarballs for the genome indices, as well as the chromosome sizes file. It only does this for hg38, because ENCODE created a STAR and RSEM index already using the applets prep-star and prep-rsem, respectively. I created my own hg19 index using these same applets, which live in my nathankw_resources project. Thus, if the genome to use is hg38, we'll find the relevent files in the $working_proj project, but if it is hg19, we'll find them in the nathankw_resources project.

encode_long_rnaseq_wf = dxpy.dxlink(dxpy.find_one_data_object(more_ok=False,project=working_proj,name="ENCODE RNA-Seq (Long) Pipeline - 1 (paired-end) replicate"))

if genome == HG38:
	encode_star_index = dxpy.dxlink(dxpy.find_one_data_object(more_ok=False,project=working_proj,name="GRCh38_v24pri_tRNAs_ERCC_phiX_starIndex.tgz")) #hg38 (extracts to 'out' folder)
	encode_rsem_index = dxpy.dxlink(dxpy.find_one_data_object(more_ok=False,project=working_proj,name="GRCh38_v24pri_tRNAs_ERCC_phiX_rsemIndex.tgz")) #hg38 (extracts to 'out' folder)
	chrom_sizes_file = dxpy.dxlink(dxpy.find_one_data_object(more_ok=False,project=working_proj,name="GRCh38_EBV.chrom.sizes"))
elif genome == HG19:
	encode_star_index = dxpy.dxlink(dxpy.find_one_data_object(more_ok=False,project=NATHANKW_RESOURCES_PROJ,name="GRCh38_v24pri_tRNAs_ERCC_phiX_starIndex.tgz")) #hg38 (extracts to 'out' folder)
	encode_rsem_index = dxpy.dxlink(dxpy.find_one_data_object(more_ok=False,project=NATHANKW_RESOURCES_PROJ,name="hg19_v19_SRM2374_Sequence_v1_rsemIndex.tgz")) #hg38 (extracts to 'out' folder)
	chrom_sizes_file = dxpy.dxlink(dxpy.find_one_data_object(more_ok=False,project=NATHANKW_RESOURCES_PROJ,name="GRCh38_EBV.chrom.sizes"))
else:
	raise Exception("Unsupported genome {genome}.".format(genome=genome))
	
#chrom_sizes_file has two columns:
	#1) chromosome name
	#2) chromosome size
#The chromosomes making up the chrom_sizes_file come from the star genome index, and includes the ERCC92 data set.

def filter_dxfiles_by_prop(dxfiles,prop,value):
	"""
	Args : dxfiles - a dict containing DXFile objects as keys. The value of each key is a dict. containing the files properties in DNAnexus.
	Returns : dict.
	"""
	res = {}
	for i in dxfiles:
		props = dxfiles[i]
		if value == props[prop]:
			res[i] = dxfiles[i]
	return res

def getReadNumberFastqs(num,dxfiles):
	"""
	Args : dxfiles - a dict containing DXFile objects as keys. The value of each key is a dict. containing the files properties in DNAnexus.
	Returns : list of DNAnexus FASTQ file IDs.
	"""
	num = str(num)
	res = []
	for i in dxfiles:
		if dxfiles[i]["read"] == num:
			res.append(i.id)
	return res
	
#Select the $working_proj project
current_project = dxpy.DXProject(dxid=working_proj)

all_fastq_dxfiles = {}
for proj_id in sequencing_projects:
	dxsr = du.DxSeqResults(dx_username="nathankw",dx_project_id=proj_id,billing_account_id="org-cescg")
	all_fastq_dxfiles[proj_id] = dxsr.get_fastq_files_props()


barcodes_dico = {}
for barcode in barcodes:
	barcode_d = {}
	barcode_d["forward"] = []
	barcode_d["reverse"] = []
	for proj_id in all_fastq_dxfiles:
		filtered = filter_dxfiles_by_prop(all_fastq_dxfiles[proj_id],"barcode",barcode)
		if not filtered: 
			continue #barcode not in this project
		for f in filtered:
			read_num = filtered[f]["read"]
			if read_num == "1":
				barcode_d["forward"].append(dxpy.dxlink(project_id=f.project,object_id=f.id))
			elif read_num == "2":
				barcode_d["reverse"].append(dxpy.dxlink(project_id=f.project,object_id=f.id))
			else:
				raise Exception("Unknown read number {num} for file {filename}.".format(num=read_num,file=f.id))
	barcodes_dico[barcode] = barcode_d

set_barcodes = set(barcodes)
set_barcodes_found = set(barcodes_dico)	
set_diff = set_barcodes - set_barcodes_found
if set_diff:
	raise Exception("Some barcodes not found: {set_diff}.".format(set_diff=set_diff))

for barcode in barcodes_dico:
	print(barcode)
	file_ids = barcodes_dico[barcode]
	first_file_id = dxpy.DXFile(file_ids["forward"][0]) #doens't matter which file we pick from the file_ids list, as they all have the same lab_* props.
	first_file_props = first_file_id.get_properties()
	patient_id = first_file_props["lab_patient_id"]
	if not patient_id:
		raise Exception("Property 'lab_patient_id' not set for file {first_file_id}.".format(first_file_id=first_file_id))
	forward_files = file_ids["forward"]
	reverse_files = file_ids["reverse"]
	#pdb.set_trace()
	if len(forward_files) != len(reverse_files):
		raise Exception("For barcode {barcode}, the number of forward files ({f_num}) doesn't match the number of reverse read files ({r_num}).".format(barcode=barcode,f_num=len(forward_files),r_num=len(reverse_files)))
	elif len(forward_files) != num_tech_reps:
		raise Exception("For barcode {barcode}, there aren't {reps} FASTQ files.".format(barcode=barcode,reps=num_tech_reps))

	destination_folder = "/encode_long_rnaseq/{patient_id}/{barcode}".format(patient_id=patient_id,barcode=barcode)
	current_project.new_folder(folder=destination_folder,parents=True) #no return value
	workflow_input = { "0.reads1":forward_files,"0.reads2":reverse_files,"0.star_index":encode_star_index,"1.chrom_sizes":chrom_sizes_file,"2.rsem_index":encode_rsem_index}
	job_name = "_".join([patient_id,barcode,encode_long_rnaseq_wf.id])
#		#run the wf
	job_properties = {"lab_patient_id":patient_id,"barcode":barcode}
	encode_long_rnaseq_wf.run(debug={"debugOn":["AppError","AppInternalError"]},workflow_input=workflow_input,project=working_proj,folder=destination_folder,name=job_name,properties=job_properties)
	break
#		#cmd = "dx run --ssh --debug-on AppError,AppInternalError --destination {destination} " + encode_long_rnaseq_wfid + " -istage-BxFZK780VBPvq9FbXQFYz4gG.reads1={lane1_f} -istage-BxFZK780VBPvq9FbXQFYz4gG.reads1={lane5_f} \
#		#				-istage-BxFZK780VBPvq9FbXQFYz4gG.reads2={lane1_r} -istage-BxFZK780VBPvq9FbXQFYz4gG.reads2={lane5_r} \
#		#				-istage-BxFZK780VBPvq9FbXQFYz4gG.star_index={encode_star_index}".format(destination=destination,lane1_f=lane1_f,lane5_f=lane5_f,lane1_r=lane1_r,lane5_r=lane5_r,star_genome_index_with_ercc=star_genome_index_with_ercc)
