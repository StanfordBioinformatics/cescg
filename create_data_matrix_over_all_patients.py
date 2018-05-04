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


description = "Runs the DNAnexus App called rsem-generate-data-matrix that I wrote in order to create the gene and isoform quantification matrices for the various conditions of each patient."
parser = argparse.ArgumentParser(description=description,formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-p","--dx-project-id",required=True,help="The DNAnexus project ID of the project containing the analysis results from the star-rsem pipeline that outputs RSEM expression quantification files for genes and isoforms.")
parser.add_argument("-f","--patient-folders-path",required=True,help="The folder path in the DNAnexus project specified by --dx-project-id that contains a folder for each patient. Each patient folder contains a folder per barcode/condition. It is assumed that the star-rsem analysis results are located here.")
parser.add_argument("--outdir",required=True,help="The full path to the folder in the specified DNAnexus project to output the results. Path must begin with a '/'.")

args = parser.parse_args()
dx_proj_id = args.dx_project_id
patient_folders_path = args.patient_folders_path
outdir = args.outdir
if not outdir.startswith("/"):
	raise Exception("--outdir must be fully qualified, starting with a '/'.")

p = dxpy.DXProject(dx_proj_id)
patient_folders = p.list_folder(folder=patient_folders_path)["folders"]
gene_files = []
isoform_files = []
for i in patient_folders:
	patient_id = os.path.basename(i)
	barcodes_folders = p.list_folder(folder=i)["folders"]
	for j in barcodes_folders:
		barcode = os.path.basename(j)
		gene_quant_file = dxpy.find_one_data_object(project=dx_proj_id,folder=j,name="*.genes.results",name_mode="glob")	
		#result is a dict of the form {u'project': u'project-BxZpbXj0V610b5Q6x1FV80gb', u'id': u'file-By3Z6fQ0ZP2jQVGz2jKQ61k5'}
		new_gene_filename = "{patient_id}_{barcode}.genes.results".format(patient_id=patient_id,barcode=barcode)
		dxpy.api.file_rename(object_id=gene_quant_file["id"],input_params={"project": gene_quant_file["project"], "name": new_gene_filename})
		gene_files.append(dxpy.dxlink(gene_quant_file))
		isoform_quant_file = dxpy.find_one_data_object(project=dx_proj_id,folder=j,name="*.isoforms.results",name_mode="glob")
		new_isoform_filename = "{patient_id}_{barcode}.isoforms.results".format(patient_id=patient_id,barcode=barcode)
		dxpy.api.file_rename(object_id=isoform_quant_file["id"],input_params={"project": isoform_quant_file["project"], "name": new_isoform_filename})
		isoform_files.append(dxpy.dxlink(isoform_quant_file))

gene_app_input = { "results": [gene_files] }
gene_job_name = "_".join(["genes",rsem_data_matrix_app.name])
print("Running app {} over all patients for gene expression.".format(rsem_data_matrix_app.name))
rsem_data_matrix_app.run(app_input=gene_app_input,project=dx_proj_id,folder=outdir,name=gene_job_name)

isoform_app_input = { "results": [isoform_files] }
isoform_job_name = "_".join(["isoforms",rsem_data_matrix_app.name])
print("Running app {} over all patients for isoform expression.".format(rsem_data_matrix_app.name))
rsem_data_matrix_app.run(app_input=isoform_app_input,project=dx_proj_id,folder=outdir,name=isoform_job_name)
