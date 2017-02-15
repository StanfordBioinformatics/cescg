#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dxpy
import pdb

joseph_wu_dx_project_id = "project-BxZpbXj0V610b5Q6x1FV80gb"

rsem_app = dxpy.DXApplet(project=joseph_wu_dx_project_id,dxid="applet-ByBpzZj0v3Vb85gqXkvQ11ZF")

rsem_index = dxpy.dxlink(project_id=joseph_wu_dx_project_id,object_id="file-Bxyp5zj0Kf6F7K2b546XPk17")


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
		workflow_input = { "0.reads1":[lane1_f,lane5_f],"0.reads2":[lane1_r,lane5_r],"0.star_index":star_genome_index_with_ercc,"1.chrom_sizes":chrom_sizes_file,"2.rsem_index":rsem_index}
		job_name = "_".join([patient_id,barcode,encode_long_rnaseq_wf.id])
		#run the wf
		job_properties = {"patient_id":patient_id,"barcode":barcode}
		encode_long_rnaseq_wf.run(debug={"debugOn":["AppError","AppInternalError"],workflow_input=workflow_input,project=joseph_wu_dx_project_id,folder=destination_folder,name=job_name,properties=job_properties)
		#cmd = "dx run --ssh --debug-on AppError,AppInternalError --destination {destination} " + encode_long_rnaseq_wfid + " -istage-BxFZK780VBPvq9FbXQFYz4gG.reads1={lane1_f} -istage-BxFZK780VBPvq9FbXQFYz4gG.reads1={lane5_f} \
		#				-istage-BxFZK780VBPvq9FbXQFYz4gG.reads2={lane1_r} -istage-BxFZK780VBPvq9FbXQFYz4gG.reads2={lane5_r} \
		#				-istage-BxFZK780VBPvq9FbXQFYz4gG.star_index={star_genome_index_with_ercc}".format(destination=destination,lane1_f=lane1_f,lane5_f=lane5_f,lane1_r=lane1_r,lane5_r=lane5_r,star_genome_index_with_ercc=star_genome_index_with_ercc)


		
