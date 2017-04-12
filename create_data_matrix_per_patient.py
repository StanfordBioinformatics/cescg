#!/usr/bin/env python

###
#Nathaniel Watson
#2017-04-11
#nathankw@stanford.edu
###

import os
import argparse
import dxpy


rsem_data_matrix_app = dxpy.DXApp(name="rsem-generate-data-matrix")


description = "howdy"
parser = argparse.ArgumentParser(description=description,formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-p","--dx-project-id",required=True,help="The DNAnexus project ID of the project containing the analysis results from the star-rsem pipeline that outputs RSEM expression quantification files for genes and isoforms.")
parser.add_argument("-f","--patient-folders-path",required=True,help="The folder path in the DNAnexus project specified by --dx-project-id that contains a folder for each patient. Each patient folder contains a folder per barcode/condition. It is assumed that the star-rsem analysis results are located here.")
parser.add_argument("-c","--num-conditions",type=int,required=True,help="The number of conditions per patient. This should match the number of barcodes (i.e. the number of barcode folders in each patient folder). A check will be performed to make sure that each patient has this many RSEM gene result files and this number of isoform result files.")

args = parser.parse_args()
dx_proj_id = args.dx_project_id
patient_folder_path = args.patient_folders_path
num_conditions = args.num_conditions

dx_proj_id = "project-BxZpbXj0V610b5Q6x1FV80gb" #Joseph_Wu
patient_folders_path = "/encode_long_rnaseq/part2_cip1_aim4/"

p = dxpy.DXProject(dx_proj_id)
patient_folders = p.list_folder(folder=patient_folders_path)["folders"]
for i in patient_folders:
	patient_id = os.path.basename(i)
	barcodes_folders = p.list_folder(folder=i)["folders"]
	gene_files = []
	isoform_files = []
	for j in barcodes_folders:
		barcode = os.path.basename(j)
		gene_quant_file = dxpy.find_one_data_object(project=dx_proj_id,folder=j,name="*.genes.results",name_mode="glob")	
		gene_files.append(dxpy.dxlink(gene_quant_file))
		isoform_quant_file = dxpy.find_one_data_object(project=dx_proj_id,folder=j,name="*.isoforms.results",name_mode="glob")
		isoform_files.append(dxpy.dxlink(isoform_quant_file))
	len_gene_files = len(gene_files)
	len_isoform_files = len(isoform_files)
	if len_gene_files != num_conditions:
		raise Exception("Patient folder {} only has {} RSEM gene result files. Expected {} since that is the number of conditions.".format(i,len_gene_files,num_conditions))
	elif len_isoform_files != num_conditions:
		raise Exception("Patient folder {} only has {} RSEM isoform result files. Expected {} since that is the number of conditions.".format(i,len_isoform_files,num_conditions))


	job_properties = {"lab_patient_id": patient_id}

	gene_app_input = { "results": [gene_files] }
	gene_job_name = "_".join(["genes",patient_id,rsem_data_matrix_app.name])
	print("Running app {} on patient {} for gene expression.".format(rsem_data_matrix_app.name,patient_id))
	rsem_data_matrix_app.run(app_input=gene_app_input,project=dx_proj_id,folder=i,name=gene_job_name)

	isoform_app_input = { "results": [isoform_files] }
	isoform_job_name = "_".join(["isoforms",patient_id,rsem_data_matrix_app.name])
	print("Running app {} on patient {} for isoform expression.".format(rsem_data_matrix_app.name,patient_id))
	rsem_data_matrix_app.run(app_input=isoform_app_input,project=dx_proj_id,folder=i,name=isoform_job_name)
