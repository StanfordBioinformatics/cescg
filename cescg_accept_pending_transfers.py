#!/usr/bin/env python

###
#Nathaniel Watson
#Stanford School of Medicine
#August 17, 2016
#nathankw@stanford.edu
###

import os
import socket
import sys
import subprocess
import logging
from argparse import ArgumentParser

import dxpy

import scgpm_seqresults_dnanexus.dnanexus_utils

LOG_DIR = "/data/cirm/submit/stanford/software/Log"
SCRIPT_NAME = os.path.basename(__file__)
LOG_FILE = os.path.join(LOG_DIR,"log_" + os.path.splitext(SCRIPT_NAME)[0] + ".txt")
#The environment module gbsc/gbsc_dnanexus/current should also be loaded in order to log into DNAnexus

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:   %(message)s')
chandler = logging.StreamHandler(sys.stdout)
chandler.setLevel(logging.INFO)
chandler.setFormatter(formatter)
logger.addHandler(chandler)

fhandler = logging.FileHandler(filename=LOG_FILE,mode="a")
fhandler.setLevel(logging.INFO)
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)


ORG = "org-cescg" #The DX org to bill each transferred project to.
USER = "nathankw" #The DX admin  user in ${ORG} to transfer each project to.
ACCESS_LEVEL = "ADMINISTER" #The DX access level that ${USER} should have on each transferred project.
ERROR_USER_EMAIL = "nathankw@stanford.edu"
ERROR_ADDITIONAL_EMAILS = ["rvnair@stanford.edu"] 
ERROR_EMAILS = [ERROR_USER_EMAIL] + ERROR_ADDITIONAL_EMAILS #Who to notify when downloading a transferred project fails.
#SUCCESS_EMAIL = "cescg-scgpm-seqdata@lists.stanford.edu"
SUCCESS_EMAIL = "cescg-scgpm-seqdata@lists.stanford.edu" #Who to notify of each successfully transferred and downloaded project.
QUEUE = "CESCG" #Look for DX projects in transfer that have the 'queue' property set to this.
SHARE_WITH_ORG = "CONTRIBUTE" #After accepting project transfers, share with ${ORG} with this access level.
OUTPUT_DIR = "/data/cirm/submit/stanford/Labs" #Top-level directory where transferred projects are downloaded to.
HOSTNAME = socket.gethostname()


description = "Accepts DNAnexus projects pending transfer to the CESCG org, then downloads each of the projects to the local host at {output_dir}.".format(output_dir=OUTPUT_DIR)
description += " For each successfully transfer project that is downloaded, an email will sent out to {addr} for notification,".format(addr=SUCCESS_EMAIL)
description == " and in DNAnexus a project property will be added to the project; this property is 'scHub' and will be set to True to indicate that the project was downloaded to SCHub."
description += " For each download that fails, and email will be sent out to {addrs} for notification.".format(addrs=",".join(ERROR_EMAILS))
description += " See more details at https://docs.google.com/document/d/1ykBa2D7kCihzIdixiOFJiSSLqhISSlqiKGMurpW5A6s/edit?usp=sharing and https://docs.google.com/a/stanford.edu/document/d/1AxEqCr4dWyEPBfp2r8SMtz8YE_tTTme730LsT_3URdY/edit?usp=sharing."

parser = ArgumentParser(description=description)
parser.parse_args()

#accept pending transfers
transferred = scgpm_seqresults_dnanexus.dnanexus_utils.accept_project_transfers(dx_username=USER,access_level=ACCESS_LEVEL,queue=QUEUE,org=ORG,share_with_org=SHARE_WITH_ORG)
#transferred is a dict. identifying the projects that were transferred to the specified billing account. Keys are the project IDs, and values are the project names.
logger.info("The following projects were transferred to {org}:".format(org=ORG))
logger.info(transferred)

for proj_id in transferred:
	try:
		dxsr = scgpm_seqresults_dnanexus.dnanexus_utils.DxSeqResults(dx_username=USER,dx_project_id=proj_id,billing_account_id=ORG)
		proj = dxpy.DXProject(dxsr.dx_project_id)
		proj_id_name = "{proj_id} {proj_name}".format(proj_id=proj.id,proj_name=proj.name)
		logger.info("Preparing to download {proj_id_name}.".format(proj_id_name=proj_id_name))
		proj_properties = proj.describe(input_params={"properties": True})["properties"]
		lab = proj_properties["lab"]
		download_dir = os.path.join(OUTPUT_DIR,lab)
		dxsr.download_project(download_dir=download_dir)
		body = "DNAnexus project {proj_id_name} for lab {lab} has successfully been downloaded to {HOSTNAME}.".format(proj_id_name=proj_id_name,lab=lab,HOSTNAME=HOSTNAME)
		logger.info(body)
		subject = "CESCG: New DNAnexus SeqResults for {proj_name}".format(proj_name=proj.name)
		subprocess.check_call("echo {body} | mail -s {subject} {TO}".format(body=body,subject=subject,TO=SUCCESS_EMAIL))
		proj_properties.update({"scHub":True})
		dxpy.api.project_set_properties(object_id=proj_id,input_params={"properties": proj_properties})
	except Exception as e:
		logger.exception(e.message)
		logger.critical("Sending email with exception details to {}".format(ERROR_EMAILS))
		subject = HOSTNAME + ":" + SCRIPT_NAME + " Error"
		cmd = "echo {msg} | mail -s {subject} {TO}".format(msg=e.message,subject=subject,TO=ERROR_EMAILS)
		subprocess.check_call(cmd=cmd,shell=True)	
