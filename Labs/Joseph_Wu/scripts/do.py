#!/bin/env python

import dxpy

def isFastqForwardOrReverse(fastq):
	if "_R1." in fastq:
		return 1
	elif "_R2." in fastq:
		return 2
	else:
		raise Exception("Can't determine orientation of FASTQ file {fastq}.".format(fastq=fastq))

def getBarcodeFromFile(fastq):
	tokens = fastq.split("_")
	barcode = tokens[-2]
	if "-" not in barcode:
		raise Exception("Can't parse barcode out of FASTQ file name {fastq}.".format(fastq=fastq))

#Select the Joseph_Wu project
p = dxpy.DXProject(dxid="project-BxZpbXj0V610b5Q6x1FV80gb")
lane1_objects = p.list_folder("/160510_COOPER_0034_BH7K2MBBXX_L1/stage0_bcl2fastq/fastqs",only="objects")["objects"]
#objects is a list of dicts of the form [{u'id': u'file-BvpGgv003gVbz7423x5kj480'}]

lane1_file_dict = {}
for f in lane1_objects:
	dxfile = dxpy.DXFile(f)
	name = dxfile.name
	barcode = getBarcodeFromFile(fastq=name)
	orientation = isFastqForwardOrReverse(fastq=name)
	if orientation == 1:
	lane1_file_dict[name] = dxfile.id


lane5_file_dict = {}
lane5_objects = p.list_folder("/160510_COOPER_0034_BH7K2MBBXX_L5/stage0_bcl2fastq/fastqs",only="objects")["objects"]
for f in lane5_objects:
	dxfile = dxpy.DXFile(f)
	name = dxfile.name
	lane5_file_dict[name] = dxfile.id

