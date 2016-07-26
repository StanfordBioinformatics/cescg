import os
import dxpy

class NoControlBarcode(Exception):
	pass

jo_wu_project = "project-BxZpbXj0V610b5Q6x1FV80gb"

control_barcodes = ["ATTACTCG-AGGCTATA","ATTACTCG-TAAGATTA","TCCGGAGA-AGGATAGG","TCCGGAGA-TAAGATTA","CGCTCATT-AGGCTATA"]

def extractControlBarcode(lis):
	"""
	Function : Given a list of barcodes, extracts the one that is a control and removes it from the list.
	Args : lis - list of barcodes. 
	Returns : str. The control barcode. 
	"""
	control = False
	for i in range(len(lis)):
		i_barcode = lis[i] #barcode is the full folder path to the barcode folder
		for j in range(len(control_barcodes)):
			j_barcode = control_barcodes[j]
			if i_barcode.endswith(j_barcode):
				control = lis.pop(i)
				break
		if control:
			break
	if not control:
		raise NoControlBarcode("No control found")
	return control

p = dxpy.DXProject(jo_wu_project)
patient_folders = p.list_folder(only="folders",folder="/encode_long_rnaseq")["folders"]
for pf in patient_folders:
	patient_id = os.path.split(pf)[-1]
  barcode_folders = p.list_folder(folder=pf,only="folders")["folders"]
	if len(barcode_folders) != 3:
		raise Exception("Expected 3 barcode folders! Check patient folder {pf}.".format(pf=pf))
	try:
		control_barcode_folder = extractControlBarcode(barcode_folders)
	except NoControlBarcode as n:
		sys.stderr.write("Error while processing patient folder {pf}.".format(pf=pf)) 
		raise n
	#now barcode_folders is the same, minus the presence of the control barcode
	for bf in barcode_folders:
		run_gene_ebseq(treatment_folder=bf,control_folder=control_barcode_folder,patient_id=patient_id)
		run_isoform_ebseq(treatent_folder=bf,control_folder=control_barcode_folder,patient_id=patient_id)


def run_gene_ebseq(treatment_folder,control_folder,patient_id):
	"""
	Runs the 'rsem-ebseq gene expression' workflow I wrote.
	"""
	gene_glob = "*.genes.results"
	quant_file = dxpy.find_data_object(more_ok=False,project=jo_wu_project,folder=technical_rep_folder,name=gene_glob,name_mode="glob")
	control_quant_file = dxpy.find_data_object(more_ok=False,project=jo_wu_project,folder=control_folder,name=gene_glob,name_mode="glob")
	#the quant_files are the isoforms gene expression files created by rsem-calculate-expression
	treatment_barcode = os.path.split(treatment_folder)[-1]
	control_barcode = os.path.split(control_folder)[-1]
	wf = dxpy.DXWorkflow(project="project-BxxYqbQ0v3VQz5z2bvFyF6YV",dxid="workflow-ByBvBkj0v3VkyPVZfVvxg2Q3")
	destination_folder = os.path.join(treatment_folder,"ebseq")
	workflow_input = {"0.results":[quant_file,control_quant_file],"1.conditions": "1,1"}
	job_properties = {"patient_id":patient_id,"control_barcode":control_barcode,"treatment_barcode":treatment_barcode}
	job_name = "_".join([patient_id,treatment_barcode,control_barcode,wf.name])
	wf.run(debug={"debugOn":["AppError","AppInternalError"],workflow_input=workflow_input,project=joseph_wu_project,folder=destination_folder,name=job_name,properties=job_properties)
	

def run_isoform_ebseq(treatment_folder,control_folder,patient_id):
	"""
	Runs the 'rsem-ebseq isoform expression' workflow I wrote.
	"""
	isoform_glob = "*.isoforms.results"
	quant_file = dxpy.find_one_data_object(more_ok=False,project=jo_wu_project,folder=treatment_folder,name=isoform_glob,name_mode="glob")
	control_quant_file = dxpy.find_data_object(more_ok=False,project=jo_wu_project,folder=control_folder,name=isoform_glob,name_mode="glob")
	#the quant_files are the isoforms gene expression files created by rsem-calculate-expression
	treatment_barcode = os.path.split(treatment_folder)[-1]
	control_barcode = os.path.split(control_folder)[-1]
	wf = dxpy.DXWorkflow(project="project-BxxYqbQ0v3VQz5z2bvFyF6YV",dxid="workflow-ByBq29Q0v3VfxzgV043QZ57J")
	destination_folder = os.path.join(treatment_folder,"ebseq")
	transcripts_file = dxpy.DXFile(project-BxZpbXj0V610b5Q6x1FV80gb:file-ByBpjPQ0V61585gqXkvQ11Z5)
	workflow_input = {"0.results":[quant_file,control_quant_file],"1.input_fasta_file":dxpy.dxlink(transcripts_file),"1.output_name":"isoforms.results","2.conditions": "1,1"}
	job_properties = {"patient_id":patient_id,"control_barcode":control_barcode,"treatment_barcode":treatment_barcode}
	job_name = "_".join([patient_id,treatment_barcode,control_barcode,wf.name])
	wf.run(debug={"debugOn":["AppError","AppInternalError"],workflow_input=workflow_input,project=joseph_wu_project,folder=destination_folder,name=job_name,properties=job_properties)
	
	
    #ebseq_folder = os.path.join(barcode_folder,"ebseq")
    #p.new_folder(ebseq_folder)
				
