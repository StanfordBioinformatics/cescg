#!/bin/env python

import dxpy
import pdb

joseph_wu_dx_project_id = "project-BxZpbXj0V610b5Q6x1FV80gb"
encode_long_rnaseq_wf = dxpy.DXWorkflow(project=joseph_wu_dx_project_id,dxid="workflow-By2Yq7j0V6119PjY2VyxY7Xy") #wfid stands for workflow ID
star_genome_index_with_ercc = dxpy.dxlink(project_id=joseph_wu_dx_project_id,object_id="file-Bxv6kJj0Vb9vKZq9G5gX0ffk")


def createFileDict(lane_objects):
	"""
	Args : lane_objects - a list of dicts of the form [{u'id': u'file-BvpGgv003gVbz7423x5kj480'}]
	"""
	dico = {}
	for f in lane_objects:
		file_id = f["id"]
		dxfile = dxpy.DXFile(file_id)
		name = dxfile.name
		if "_noBarcode_" in name:
			continue
		props = dxfile.get_properties()
		barcode = props["barcode"]
		patient_id = props["patient_id"]
		orientation = int(props["read"])
		if patient_id not in dico:
			dico[patient_id] = {}
		if barcode not in dico[patient_id]:
			dico[patient_id][barcode] = {}
		if orientation == 1:
			dico[patient_id][barcode]["forward"] = {"dxid": file_id,"name":name}
		elif orientation == 2:
			dico[patient_id][barcode]["reverse"] = {"dxid": file_id,"name":name}
		else:
			raise Exception("Unknown read orientation '{orientation}' for file {name}. Vale of the 'read' property must be in the set (1,2).".format(orientation=orientation,name=name))
	return dico

def verifyLaneDict(dico,lane):
	"""
	Args: dico - A dict. returned by the function createFileDict().
				lane - int. The lane number represented by dico (in this program, that's either 1 or 5.
	"""
	
	for patient_id in dico:
		#check that each patient has 3 barcodes
		patient_barcodes = dico[patient_id].keys()
		if len(patient_barcodes) != 3:
			raise Exception("Lane {lane} patient {patient_id} does not have 3 barcodes!".format(lane=lane,patient_id=patient_id))
		#check that each patient has, for each barcode, a forward and a reverse read file
		for barcode in patient_barcodes:
			read_dico = dico[patient_id][barcode]
			if "forward" not in read_dico:
				raise Exception("Lane {lane} patient {patient_id} barcode {barcode} does not have a forward read file.".format(lane=lane,patient_id=patient_id,barcode=barcode))
			if "reverse" not in read_dico:
				raise Exception("Lane {lane} patient {patient_id} barcode {barcode} does not have a reverse read file.".format(lane=lane,patient_id=patient_id,barcode=barcode))

#Select the Joseph_Wu project
project = dxpy.DXProject(dxid=joseph_wu_dx_project_id)

lane1_objects = project.list_folder("/160510_COOPER_0034_BH7K2MBBXX_L1/stage0_bcl2fastq/fastqs",only="objects")["objects"]
lane5_objects = project.list_folder("/160510_COOPER_0034_BH7K2MBBXX_L5/stage0_bcl2fastq/fastqs",only="objects")["objects"]
#objects is a list of dicts of the form [{u'id': u'file-BvpGgv003gVbz7423x5kj480'}]

lane1_dico = createFileDict(lane1_objects)
verifyLaneDict(dico=lane1_dico,lane=1)
lane5_dico = createFileDict(lane5_objects)
verifyLaneDict(dico=lane5_dico,lane=5)


for patient_id in lane1_dico:
	patient = lane1_dico[patient_id]
	barcodes = patient.keys()
	for barcode in barcodes:
		lane1_f = dxpy.dxlink(lane1_dico[patient_id][barcode]["forward"]["dxid"])
		lane1_r = dxpy.dxlink(lane1_dico[patient_id][barcode]["reverse"]["dxid"])
		lane5_f = dxpy.dxlink(lane5_dico[patient_id][barcode]["forward"]["dxid"])
		lane5_r = dxpy.dxlink(lane5_dico[patient_id][barcode]["reverse"]["dxid"])
		destination_folder = "/encode_long_rnaseq/{patient_id}/{barcode}".format(patient_id=patient_id,barcode=barcode)
		project.new_folder(folder=destination_folder,parents=True) #no return value
		workflow_input = { "0.reads1":[lane1_f,lane5_f],"0.reads2":[lane1_r,lane5_r],"0.star_index":star_genome_index_with_ercc}
		job_name = "_".join([patient_id,barcode,encode_long_rnaseq_wf.id])
		#run the wf
		job_properties = {"patient_id":patient_id,"barcode":barcode}
		encode_long_rnaseq_wf.run(workflow_input=workflow_input,project=joseph_wu_dx_project_id,folder=destination_folder,name=job_name,properties=job_properties)
		#cmd = "dx run --ssh --debug-on AppError,AppInternalError --destination {destination} " + encode_long_rnaseq_wfid + " -istage-BxFZK780VBPvq9FbXQFYz4gG.reads1={lane1_f} -istage-BxFZK780VBPvq9FbXQFYz4gG.reads1={lane5_f} \
		#				-istage-BxFZK780VBPvq9FbXQFYz4gG.reads2={lane1_r} -istage-BxFZK780VBPvq9FbXQFYz4gG.reads2={lane5_r} \
		#				-istage-BxFZK780VBPvq9FbXQFYz4gG.star_index={star_genome_index_with_ercc}".format(destination=destination,lane1_f=lane1_f,lane5_f=lane5_f,lane1_r=lane1_r,lane5_r=lane5_r,star_genome_index_with_ercc=star_genome_index_with_ercc)


		
