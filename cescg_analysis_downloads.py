#/usr/bin/env python

import argparse
import datetime
import json
import re
import dxpy

#  1. Create a DXProject instance for the project of interest
#  2. List the folder contents at the root level
#  3. List the folder contains of a specific folder.
#  4. Download files of interest for every folder in the project.

def get_parser():
    parser = argparse.ArgumentParser(description="Downloads VCF and BAM analsyis files from every folder of the specified DNAnexus project.")
    parser.add_argument("-p", "--project-id", required=True, help="The ID of the DNANexus project (i.e. project-F365G500gXF35X062JF16Q2P).")
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    proj_id = args.project_id
    proj = dxpy.DXProject(proj_id)
    folders = proj.list_folder()["folders"]
    
    # Get files in first folder:
    #>>> files = proj.list_folder(folders[0], describe=True)["objects"]

    # files is a list of dicts, where each dict is formatted as shown below:

    # >>> print(json.dumps(folders[0], indent=4))
    #    {
    #        "describe": {
    #            "archivalState": "live", 
    #            "name": "284.bai", 
    #            "links": [], 
    #            "tags": [], 
    #            "media": "application/octet-stream", 
    #            "created": 1489805779000, 
    #            "modified": 1489812389016, 
    #            "class": "file", 
    #            "project": "project-F365G500gXF35X062JF16Q2P", 
    #            "state": "closed", 
    #            "folder": "/284", 
    #            "sponsored": false, 
    #            "createdBy": {
    #                "job": "job-F366fZ80gXFKZ5KF2vZ7v5V8", 
    #                "executable": "app-F2pFJ800bpfZqzYk5PF5y9Pb", 
    #                "user": "user-rvnair"
    #            }, 
    #            "hidden": false, 
    #            "id": "file-F36B3Zj0PF3b37Qf8ybXQvYY", 
    #            "types": [], 
    #            "size": 8902224
    #        }, 
    #        "id": "file-F36B3Zj0PF3b37Qf8ybXQvYY"
    #    }
    

    # Create regex to capture BAM and VCF files of interest:
    reg = re.compile(r'(\.vcf\.)|(\.recalibrated\.bam)')
    #reg = re.compile(r'\.bai')
    
    # Create log file
    fout = open("log_cescg_analysis_downloads.txt",'wa')
    fout.write(str(datetime.datetime.now()) + "\n\n")
    
    # Loop through all folders in the project
    for fold in folders:
        files = proj.list_folder(fold,describe=True)["objects"]
        for f in files:
            file_name = f["describe"]["name"]  
            if reg.search(file_name):
                msg = "Downloading file '{}' from '{}'\n.".format(file_name, proj.name + ":" + fold)
                print(msg)
                fout.write(msg + "\n")
                dxpy.download_dxfile(dxid=f["id"], filename=file_name)
                msg = "Download complete.\n"
                fout.write(msg + "\n")
                fout.flush()
    fout.close()
        
if __name__ == "__main__":
    main()
