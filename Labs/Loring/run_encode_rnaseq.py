#!/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import pdb

import dxpy

from scgpm_seqresults_dnanexus import dnanexus_utils as du #module load gbsc/scgmp_seqresults_dnanexus/current

#There are 12 patients. Each was sequenced under the following 4 conditions:
	#iPSC
	#No Treatment
	#Prevastatin, 0.1 uM
	#Carvedilol, 0.1 uM

#For each patient, for each sample, I need to run the ENCODE Long RNA-Seq pipeline on hg19. Then, I'll need to run EBSeq (rsem-run-ebseq) to calculate both gene and isoform differential expression of each medicine dose
# against the 'No Treatment' sample. I can ignore the iPSC sample I'm told, but I'll go ahead and map it. 

#Each sample was sequenced 6 times. That is, the same barcode was sequenced in 6 lanes. They are the following 6 DNAnexus projects:
#	161111_GADGET_0079_AHFNKMBBXX_L1_SW03-11-02-16 (project-F0bv6b00k49KxZvfGQG3v3qQ)
#	161111_GADGET_0079_AHFNKMBBXX_L5_SW03-11-02-16 (project-F0bxzXj0kgYq5Qzf9jp4fVB0)
#	161111_GADGET_0079_AHFNKMBBXX_L6_SW03-11-02-16 (project-F0bz9GQ0FggyF151x0BQg678)
#	161020_COOPER_0067_BHFTW2BBXX_L5_SW03-ROY01 (project-F07jGX00P0By6yk2ZkFqVz06)
#	161108_COOPER_0071_AHFNKYBBXX_L1_SW03-11-02-16 (project-F0bJ2bj05gbXG139J83jv49z)
#	161107_GADGET_0078_BHFNKGBBXX_L5_SW03-11-02-16 (project-F0b4Z3002Pf29FK60bqX7bg6)

#When running the ENCODE pipeline, I'll run it for all 6 technical replicates at the same time.


#Note that for each of the FASTQ files in DNAnexus, I added three properties:
	#1) lab_patient_id
	#2) lab_patient_group
  #3) lab_patient_condition
#That way, I'll be able to easily query for the files that I need. Below I paste in the sample data that Eric Wei provided to me. 

#lab_patient_id	lab_patient_group	lab_patient_condition	Index
#287 #1A	HCM	iPSC	ATTACTCG-AGGCTATA
#287 #1B	HCM	No Treatment	ATTACTCG-GCCTCTAT
#287 #1C	HCM	Pravastatin 0.1 µM	ATTACTCG-AGGATAGG
#287 #1D	HCM	Carvedilol 0.1 µM	ATTACTCG-TCAGAGCC
#289 #1A	HCM	iPSC	ATTACTCG-CTTCGCCT
#289 #1B	HCM	No Treatment	ATTACTCG-TAAGATTA
#289 #1C	HCM	Pravastatin 0.1 µM	ATTACTCG-ACGTCCTG
#289 #1D	HCM	Carvedilol 0.1 µM	ATTACTCG-GTCAGTAC
#297 #1A	Control	iPSC	TCCGGAGA-AGGCTATA
#297 #1B	Control	No Treatment	TCCGGAGA-GCCTCTAT
#297 #1C	Control	Pravastatin 0.1 µM	TCCGGAGA-AGGATAGG
#297 #1D	Control	Carvedilol 0.1 µM	TCCGGAGA-TCAGAGCC
#304 #1A	LVNC (DCM)	iPSC	TCCGGAGA-CTTCGCCT
#304 #1B	LVNC (DCM)	No Treatment	TCCGGAGA-TAAGATTA
#304 #1C	LVNC (DCM)	Pravastatin 0.1 µM	TCCGGAGA-ACGTCCTG
#304 #1D	LVNC (DCM)	Carvedilol 0.1 µM	TCCGGAGA-GTCAGTAC
#320 #1A	DCM	iPSC	CGCTCATT-AGGCTATA
#320 #1B	DCM	No Treatment	CGCTCATT-GCCTCTAT
#320 #1C	DCM	Pravastatin 0.1 µM	CGCTCATT-AGGATAGG
#320 #1D	DCM	Carvedilol 0.1 µM	CGCTCATT-TCAGAGCC
#372 #1A	Control	iPSC	CGCTCATT-CTTCGCCT
#372 #1B	Control	No Treatment	CGCTCATT-TAAGATTA
#372 #1C	Control	Pravastatin 0.1 µM	CGCTCATT-ACGTCCTG
#372 #1D	Control	Carvedilol 0.1 µM	CGCTCATT-GTCAGTAC
#397 #1A	HCM	iPSC	GAGATTCC-AGGCTATA
#397 #1B	HCM	No Treatment	GAGATTCC-GCCTCTAT
#397 #1C	HCM	Pravastatin 0.1 µM	GAGATTCC-AGGATAGG
#397 #1D	HCM	Carvedilol 0.1 µM	GAGATTCC-TCAGAGCC
#284 #1A	Control	iPSC	GAGATTCC-CTTCGCCT
#284 #1B	Control	No Treatment	GAGATTCC-TAAGATTA
#284 #1C	Control	Pravastatin 0.1 µM	GAGATTCC-ACGTCCTG
#284 #1D	Control	Carvedilol 0.1 µM	GAGATTCC-GTCAGTAC
#310 #1A	HCM	iPSC	ATTCAGAA-AGGCTATA
#310 #1B	HCM	No Treatment	ATTCAGAA-GCCTCTAT
#310 #1C	HCM	Pravastatin 0.1 µM	ATTCAGAA-AGGATAGG
#310 #1D	HCM	Carvedilol 0.1 µM	ATTCAGAA-TCAGAGCC
#367 #1A	DCM	iPSC	ATTCAGAA-CTTCGCCT
#367 #1B	DCM	No Treatment	ATTCAGAA-TAAGATTA
#367 #1C	DCM	Pravastatin 0.1 µM	ATTCAGAA-ACGTCCTG
#367 #1D	DCM	Carvedilol 0.1 µM	ATTCAGAA-GTCAGTAC
#301 #1A	HCM	iPSC	GAATTCGT-AGGCTATA
#301 #1B	HCM	No Treatment	GAATTCGT-GCCTCTAT
#301 #1C	HCM	Pravastatin 0.1 µM	GAATTCGT-AGGATAGG
#301 #1D	HCM	Carvedilol 0.1 µM	GAATTCGT-TCAGAGCC
#352 #1A	HCM	iPSC	GAATTCGT-CTTCGCCT
#352 #1B	HCM	No Treatment	GAATTCGT-TAAGATTA
#352 #1C	HCM	Pravastatin 0.1 µM	GAATTCGT-ACGTCCTG
#352 #1D	HCM	Carvedilol 0.1 µM	GAATTCGT-GTCAGTAC

#I'll run the ENCODE Uniform Long RNA-Seq pipeline in the Joseph_Wu DNAnexus project (project-BxZpbXj0V610b5Q6x1FV80gb) and output the results in the same project and in the folder path Joseph_Wu/encode_long_rnaseq/part2_cip1_aim4. Within that folder, there will be a subfolder named after each patient ID, i.e. 287, and a sub-folder there-within named after the barcode. 

working_proj = "project-F2YpBxQ0721Fjp343Q7bQKXx" #Loring

nathankw_resources_project_id = "project-BxxYqbQ0v3VQz5z2bvFyF6YV" 
encode_long_rnaseq_wf = dxpy.DXWorkflow(project=working_proj,dxid="workflow-F2YpGk80721FF01y1k4JG7Jz") #wfid stands for workflow ID
star_genome_index_with_ercc = dxpy.dxlink(project_id=nathankw_resources_project_id,object_id="file-F1vk6Q00J2fP7Jv79XPKY9zZ") #hg38
sequencing_projects = ["project-F0b1P4Q04fx48f2yk1j3gG61","project-F0bJ3Xj03jJF87gf94X2fv8F"]

chrom_sizes_file = dxpy.dxlink(project_id=nathankw_resources_project_id,object_id="file-F2XBxfQ0v3VXzGb642zVbxz9") #hg38
#chrom_sizes_file has two columns:
	#1) chromosome name
	#2) chromosome size
#The chromosomes making up the chrom_sizes_file come from the star genome index, and includes the ERCC92 data set.

#rsem_index = dxpy.dxlink(project_id=working_proj,object_id="file-Bxyp5zj0Kf6F7K2b546XPk17")


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
	


barcodes = ["TCCGCGAA-AGGCTATA","TCCGCGAA-GCCTCTAT","TCCGCGAA-AGGATAGG","TCCGCGAA-TCAGAGCC","TCCGCGAA-CTTCGCCT","TCCGCGAA-TAAGATTA","TCCGCGAA-ACGTCCTG","TCCGCGAA-GTCAGTAC","TCTCGCGC-AGGCTATA","TCTCGCGC-GCCTCTAT","TCTCGCGC-AGGATAGG","TCTCGCGC-TCAGAGCC","TCTCGCGC-CTTCGCCT","TCTCGCGC-TAAGATTA","TCTCGCGC-ACGTCCTG","TCTCGCGC-GTCAGTAC","AGCGATAG-AGGCTATA","AGCGATAG-GCCTCTAT","AGCGATAG-AGGATAGG","AGCGATAG-TCAGAGCC"]

current_project = dxpy.DXProject(dxid=working_proj)

#Select the Joseph_Wu project
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
	elif len(forward_files) != 2:
		raise Exception("For barcode {barcode}, there aren't 6 FASTQ files.".format(barcode=barcode))

	destination_folder = "/encode_long_rnaseq/{patient_id}/{barcode}".format(patient_id=patient_id,barcode=barcode)
	current_project.new_folder(folder=destination_folder,parents=True) #no return value
	workflow_input = { "0.reads1":forward_files,"0.reads2":reverse_files,"0.star_index":star_genome_index_with_ercc,"1.chrom_sizes":chrom_sizes_file,"2.rsem_index":star_genome_index_with_ercc}
	job_name = "_".join([patient_id,barcode,encode_long_rnaseq_wf.id])
#		#run the wf
	job_properties = {"lab_patient_id":patient_id,"barcode":barcode}
	encode_long_rnaseq_wf.run(debug={"debugOn":["AppError","AppInternalError"]},workflow_input=workflow_input,project=working_proj,folder=destination_folder,name=job_name,properties=job_properties)
#		#cmd = "dx run --ssh --debug-on AppError,AppInternalError --destination {destination} " + encode_long_rnaseq_wfid + " -istage-BxFZK780VBPvq9FbXQFYz4gG.reads1={lane1_f} -istage-BxFZK780VBPvq9FbXQFYz4gG.reads1={lane5_f} \
#		#				-istage-BxFZK780VBPvq9FbXQFYz4gG.reads2={lane1_r} -istage-BxFZK780VBPvq9FbXQFYz4gG.reads2={lane5_r} \
#		#				-istage-BxFZK780VBPvq9FbXQFYz4gG.star_index={star_genome_index_with_ercc}".format(destination=destination,lane1_f=lane1_f,lane5_f=lane5_f,lane1_r=lane1_r,lane5_r=lane5_r,star_genome_index_with_ercc=star_genome_index_with_ercc)
