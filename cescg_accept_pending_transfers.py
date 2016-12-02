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


ORG = "org-cescg"
USER = "nathankw"
USER_EMAIL = "nathankw@stanford.edu"
ALTERNATE_EMAILS = []
EMAILS = USER_EMAIL + ",".join(ALTERNATE_EMAILS)
QUEUE = "CESCG"
ACCESS_LEVEL = "ADMINISTER"
SHARE_WITH_ORG = "CONTRIBUTE"
output_dir = "/data/cirm/submit/stanford/Labs"
HOSTNAME = socket.gethostname()



description = "Accepts DNAnexus projects pending transfer to the CESCG org, then downloads each of the projects to the local host at {output_dir}.".format(output_dir=output_dir)
description += "See more details at https://docs.google.com/document/d/1ykBa2D7kCihzIdixiOFJiSSLqhISSlqiKGMurpW5A6s/edit?usp=sharing and https://docs.google.com/a/stanford.edu/document/d/1AxEqCr4dWyEPBfp2r8SMtz8YE_tTTme730LsT_3URdY/edit?usp=sharing."

parser = ArgumentParser(description=description)
parser.parse_args()

#accept pending transfers
transferred = scgpm_seqresults_dnanexus.dnanexus_utils.accept_project_transfers(dx_username=USER,access_level=ACCESS_LEVEL,queue=QUEUE,org=ORG,share_with_org=SHARE_WITH_ORG)
#transferred is a dict. identifying the projects that were transferred to the specified billing account. Keys are the project IDs, and values are the project names.
logger.info("The following projects were transferred to {org}:".format(org=ORG))
logger.info(transferred)

email_subject = HOSTNAME + ":" + SCRIPT_NAME
email_cmd = "mail -s {subject} {USER_EMAIL}".format(subject=email_subject,USER_EMAIL=USER_EMAIL)
if ALTERNATE_EMAILS:
	email_cmd += " {}".format(" ".join(ALTERNATE_EMAILS))

for proj_id in transferred:
	try:
		dxsr = scgpm_seqresults_dnanexus.dnanexus_utils.DxSeqResults(dx_username=USER,dx_project_id=proj_id,billing_account_id=ORG)
		proj = dxpy.DXProject(dxsr.dx_project_id)
		logger.info("Preparing to downloaded {proj_id} {proj_name}.".format(proj_id=proj.id,proj_name=proj.name))
		proj_properties = proj.describe(input_params={"properties": True})["properties"]
		lab = proj_properties["lab"]
		download_dir = os.path.join(OUTPUT_DIR,lab)
		dxsr.download_project(download_dir=download_dir)
		logger.info("Downloaded {proj_id} {proj_name}.".format(proj_id=proj.id,proj_name=proj.name))
	except Exception as e:
		logger.exception(e.message)
		logger.critical("Sending email with exception details to {}".format(EMAILS))
		cmd = "echo {msg} | ".format(msg=e.message) + email_cmd
		subprocess.check_call(cmd=cmd,shell=True)	
