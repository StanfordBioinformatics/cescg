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
import argparse

import dxpy

import gbsc_dnanexus.utils #module load gbsc/gbsc_dnanexus
import scgpm_seqresults_dnanexus.dnanexus_utils

#The environment module gbsc/gbsc_dnanexus/current should also be loaded in order to log into DNAnexus

#GLOBALS
INTERNAL_HOLD_PROJ_PROP = "internal_hold" #bool
LAB_PROJ_PROP = "lab"
SCHUB_DOWNLOAD_COMPLETE_PROJ_PROP = "scHub"    #bool
ERROR_EMAIL = ["nathankw@stanford.edu","rvnair@stanford.edu"] #Who to notify when downloading a transferred project fails.
SUCCESS_EMAIL = "cescg-scgpm-seqdata@lists.stanford.edu" #Who to notify of each successfully transferred and downloaded project.
HOSTNAME = socket.gethostname()
DX_LOGIN_CONF = gbsc_dnanexus.CONF_FILE

description = "Accepts DNAnexus projects pending transfer to the CESCG org, then downloads each of the projects to the local host at specified location."
description += " For each successfull project download, an email will sent out to {addr} for notification,".format(addr=SUCCESS_EMAIL)
description == " and in DNAnexus a project property will be added to the project; this property is {} and will be set to True to indicate that the project was downloaded to SCHub.".format(SCHUB_DOWNLOAD_COMPLETE_PROJ_PROP)
description += " For each download that fails, and email will be sent out to {addrs} for notification.".format(addrs=",".join(ERROR_EMAIL))
description += " See more details at https://docs.google.com/document/d/1ykBa2D7kCihzIdixiOFJiSSLqhISSlqiKGMurpW5A6s/edit?usp=sharing and https://docs.google.com/a/stanford.edu/document/d/1AxEqCr4dWyEPBfp2r8SMtz8YE_tTTme730LsT_3URdY/edit?usp=sharing."

parser = argparse.ArgumentParser(description=description,formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-u',"--dx-user-name",required=True,help="The DNAnexus login user name. An API token must have already been generated for this user and that token must have been added to the DNAnexus login configuration file located at {DX_LOGIN_CONF}.".format(DX_LOGIN_CONF=DX_LOGIN_CONF))
parser.add_argument("-p","--dx-project-ids",required=True,nargs="+",help="One or more DNAnexus project IDs.")
parser.add_argument("-d","--download-dir",required=True,help="The local directory in which to download each DNAnexus project. The path must already exist.")
parser.add_argument("-l","--log",required=True,help="The log file to append to.")
args = parser.parse_args()

dx_username = args.dx_user_name
proj_ids = args.dx_project_ids
download_dir = args.download_dir
log_file = args.log

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:   %(message)s')
chandler = logging.StreamHandler(sys.stdout)
chandler.setLevel(logging.INFO)
chandler.setFormatter(formatter)
logger.addHandler(chandler)

fhandler = logging.FileHandler(filename=log_file,mode="a")
fhandler.setLevel(logging.INFO)
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)

if not os.path.exists(download_dir):
	raise Exception("Value to --download-dir ({dd}) does not exist!".format(dd=download_dir))

for proj_id in proj_ids:
	try:
		dxsr = scgpm_seqresults_dnanexus.dnanexus_utils.DxSeqResults(dx_username=dx_username,dx_project_id=proj_id,billing_account_id=ORG)
		proj = dxpy.DXProject(dxsr.dx_project_id)
		proj_id_name = "{proj_id} {proj_name}".format(proj_id=proj.id,proj_name=proj.name)
		logger.info("Preparing to download {proj_id_name}.".format(proj_id_name=proj_id_name))
		proj_properties = proj.describe(input_params={"properties": True})["properties"]
		if INTERNAL_HOLD_PROJ_PROP in proj_properties:
			if proj_properties[INTERNAL_HOLD_PROJ_PROP].lower().strip() == "true":
				continue #don't download to SCHub at this time.
		lab = proj_properties[LAB_PROJ_PROP]
		lab_download_dir = os.path.join(download_dir,lab)
		dxsr.download_project(download_dir=lab_download_dir)
		body = "DNAnexus project {proj_id_name} for the {lab} lab has successfully been downloaded to {HOSTNAME}.".format(proj_id_name=proj_id_name,lab=lab,HOSTNAME=HOSTNAME)
		logger.info(body)
		subject = "CESCG: New DNAnexus SeqResults for {proj_name}".format(proj_name=proj.name)
		cmd = "echo {body} | mail -s {subject} {TO}".format(body=body,subject=subject,TO=SUCCESS_EMAIL)
		subprocess.check_call(cmd,shell=True)
		proj_properties.update({SCHUB_DOWNLOAD_COMPLETE_PROJ_PROP:True})
		dxpy.api.project_set_properties(object_id=proj_id,input_params={"properties": proj_properties})
	except Exception as e:
		logger.exception(e.message)
		logger.critical("Sending email with exception details to {}".format(ERROR_EMAIL))
		subject = HOSTNAME + ":" + SCRIPT_NAME + " Error"
		cmd = "echo {msg} | mail -s {subject} {TO}".format(msg=e.message,subject=subject,TO=ERROR_EMAIL)
		subprocess.check_call(cmd,shell=True)	
