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
import json

import dxpy

import scgpm_seqresults_dnanexus.dnanexus_utils

#The environment module gbsc/gbsc_dnanexus/current should also be loaded in order to log into DNAnexus
conf_file = os.path.join(os.path.dirname(__file__),"conf.json")
cfh = open(conf_file)
conf = json.load(cfh)

SCRIPT_NAME = os.path.basename(__file__)
DX_ORG_CESCG_ID = conf["dx"]["orgs"]["cescg"]["id"]
DX_USER = conf["dx"]["orgs"]["cescg"]["admin"] #The DX admin  user in ${ORG} to transfer each project to.
LOG_FILE = conf["schub_pod"]["logfile"]

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


description = "Accepts DNAnexus projects pending transfer to the CESCG org, then downloads each of the projects to the local host at the designated output directory."
description == "In DNAnexus, a project property will be added to the project; this property is 'scHub' and will be set to True to indicate that the project was downloaded to the SCHub pod."
description += "Project downloading is handled by the script download_cirm_dx-project.py, which sends out notification emails as specified in the configuration file {} in both successful and unsuccessful circomstances.".format(conf_file)
description += " See more details at https://docs.google.com/document/d/1ykBa2D7kCihzIdixiOFJiSSLqhISSlqiKGMurpW5A6s/edit?usp=sharing and https://docs.google.com/a/stanford.edu/document/d/1AxEqCr4dWyEPBfp2r8SMtz8YE_tTTme730LsT_3URdY/edit?usp=sharing."

parser = argparse.ArgumentParser(description=description,formatter_class=argparse.RawTextHelpFormatter)
parser.parse_args()

#accept pending transfers
transferred = scgpm_seqresults_dnanexus.dnanexus_utils.accept_project_transfers(dx_username=DX_USER,access_level="ADMINISTER",queue="CESCG",org=DX_ORG_CESCG_ID,share_with_org="CONTRIBUTE")
#transferred is a dict. identifying the projects that were transferred to the specified billing account. Keys are the project IDs, and values are the project names.
logger.info("The following projects were transferred to {org}:".format(org=DX_ORG_CESCG_ID))
logger.info(transferred)

if transferred: #will be an empty dict otherwise.
	transferred_proj_ids = transferred.keys()
	cmd = "download_cirm_dx-project.py -p {proj_ids}".format(proj_ids=" ".join(transferred_proj_ids))
	subprocess.check_call(cmd,shell=True)
