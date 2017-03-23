#!/usr/bin/env python

###
#Nathaniel Watson
#Stanford School of Medicine
#August 17, 2016
#nathankw@stanford.edu
###

import os
import json
import socket
import sys
import subprocess
import logging
import argparse

import dxpy

import gbsc_dnanexus.utils #module load gbsc/gbsc_dnanexus
import scgpm_seqresults_dnanexus.dnanexus_utils

#The environment module gbsc/gbsc_dnanexus/current should also be loaded in order to log into DNAnexus

conf_file = os.path.join(os.path.dirname(__file__),"conf.json")
cfh = open(conf_file)
conf = json.load(cfh)

#GLOBALS
SCRIPT_NAME = os.path.basename(sys.argv[0])
DX_USER = conf["dx"]["orgs"]["cescg"]["admin"]
DX_CESCG_ORG_ID = conf["dx"]["orgs"]["cescg"]["id"]
DOWNLOAD_DIR = conf["schub_pod"]["dx_download_root"]
LOG_FILE = conf["schub_pod"]["logfile"]
INTERNAL_HOLD_PROJ_PROP = conf["dx"]["project_props"]["internal_hold"] #bool
LAB_PROJ_PROP = conf["dx"]["project_props"]["lab"]
SCHUB_DOWNLOAD_COMPLETE_PROJ_PROP = conf["dx"]["project_props"]["scHub"]    #bool
ERROR_EMAILS = conf["dx"]["orgs"]["cescg"]["error_emails"] #Who to notify when downloading a transferred project fails.
SUCCESS_EMAIL = conf["dx"]["orgs"]["cescg"]["org_email"]  #Who to notify of each successfully transferred and downloaded project.
HOSTNAME = socket.gethostname()
DX_LOGIN_CONF = gbsc_dnanexus.CONF_FILE

description = "Downloads each of the specified DNAnexus projects to the local host at specified location."
description += " For each successfull project download, an email will sent out to {addr} for notification,".format(addr=SUCCESS_EMAIL)
description == " and in DNAnexus a project property will be added to the project; this property is {} and will be set to True to indicate that the project was downloaded to SCHub.".format(SCHUB_DOWNLOAD_COMPLETE_PROJ_PROP)
description += " For each download that fails, and email will be sent out to {addrs} for notification.".format(addrs=",".join(ERROR_EMAILS))
description += " See more details at https://docs.google.com/document/d/1ykBa2D7kCihzIdixiOFJiSSLqhISSlqiKGMurpW5A6s/edit?usp=sharing and https://docs.google.com/a/stanford.edu/document/d/1AxEqCr4dWyEPBfp2r8SMtz8YE_tTTme730LsT_3URdY/edit?usp=sharing."

parser = argparse.ArgumentParser(description=description,formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-p","--dx-project-ids",required=True,nargs="+",help="One or more DNAnexus project IDs.")
args = parser.parse_args()

proj_ids = args.dx_project_ids

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

if not os.path.exists(DOWNLOAD_DIR):
	raise Exception("Value to --download-dir ({dd}) does not exist!".format(dd=DOWNLOAD_DIR))

for proj_id in proj_ids:
	try:
		dxsr = scgpm_seqresults_dnanexus.dnanexus_utils.DxSeqResults(dx_username=DX_USER,dx_project_id=proj_id,billing_account_id=DX_CESCG_ORG_ID)
		proj = dxpy.DXProject(dxsr.dx_project_id)
		proj_id_name = "{proj_id} {proj_name}".format(proj_id=proj.id,proj_name=proj.name)
		logger.info("Preparing to download {proj_id_name}.".format(proj_id_name=proj_id_name))
		proj_properties = proj.describe(input_params={"properties": True})["properties"]
		if INTERNAL_HOLD_PROJ_PROP in proj_properties:
			if proj_properties[INTERNAL_HOLD_PROJ_PROP].lower().strip() == "true":
				continue #don't download to SCHub at this time.
		lab = proj_properties[LAB_PROJ_PROP]
		lab_download_dir = os.path.join(DOWNLOAD_DIR,lab)
		dxsr.download_project(download_dir=lab_download_dir)
		body = "DNAnexus project {proj_id_name} for the {lab} lab has successfully been downloaded to {HOSTNAME}.".format(proj_id_name=proj_id_name,lab=lab,HOSTNAME=HOSTNAME)
		logger.info(body)
		subject = "CESCG: New DNAnexus SeqResults for {proj_name}".format(proj_name=proj.name)
		cmd = "echo {body} | mail -s {subject} {TO}".format(body=body,subject=subject,TO=SUCCESS_EMAIL)
		subprocess.check_call(cmd,shell=True)
		proj_properties.update({SCHUB_DOWNLOAD_COMPLETE_PROJ_PROP:"true"})
		dxpy.api.project_set_properties(object_id=proj_id,input_params={"properties": proj_properties})
	except Exception as e:
		logger.exception(e.message)
		logger.critical("Sending email with exception details to {}".format(ERROR_EMAILS))
		subject = HOSTNAME + ":" + SCRIPT_NAME + ":" + proj_id + " Error"
		err_message = e.message
		if issubclass(e.__class__,EnvironmentError):
			err_message = e.strerror
			#EnvironmentError erros don't have a value set for the messages attribute. Instead, that value should be grabbed from the strerror attribute.
			#As stated from the Python docs, EnvironmentError is the base class for exceptions that can occur outside the Python system: IOError, OSError. When exceptions of this type are created with a 2-tuple, 
			# the first item is available on the instance's errno attribute (it is assumed to be an error number), and the second item is available on the strerror attribute
			# (it is usually the associated error message). The tuple itself is also available on the args attribute.
		cmd = "echo {msg} | mail -s \"{subject}\" \"{TO}\"".format(msg=err_message,subject=subject,TO=" ".join(ERROR_EMAILS))
		subprocess.check_call(cmd,shell=True)	
