#!/bin/env python

import os
import glob
import argparse


PATIENTS_DIR = "/data/cirm/submit/stanford/Labs/Wu/Analyses/CIP1_aim_4/encode_long_rnaseq"

description = """This script is used to fill out the MISCE module named 'data transformation' for RNA-Seq analysis. Specifically, the ENCODE RNA-Seq pipeline must of previously been run on each barcoded sample. There is an output structure that must be followed. When I run the pipeline, I output a directory tree that looks as follows:
	encode_long_rna_seq/
		patient_id/
			barcode/
				ebseq/

There can be multiple 'patient_id' folders, and multiple 'barcode' folders. The 'ebseq' folder is really optional since I probably won't be calling EBseq for differential expression analysis going forwards. Calling EBSeq isn't part of the ENCODE Long-RNA Seq workflow on DNAnexus, and it's something that I originally added to extend it. 

The main analysis files that this adds to the "data transformation" module are:
	1) The transcriptome BAM,
	2) The STAR log,
	3) The plus strand BigWig file,
	4) The minus strand BigWig file,
	5) The output of rsem-calculate-expression. There are two files that quantify expression at both the gene level and the isoform level:
			- the genes.results file
			- the isoforms.results file
	6) (Defunct) Optionally the ebseq results. This is the part I added where I have an applet on DNAnexus that wraps the rsem-run-ebseq command to
		 perform differential expression at both the gene level and the isoform level. 

Note that this script has been run so far with the Snyder/Wu CIP1 project "CIP1 aim 4". The DNAnexus project containing the results is called "Joseph Wu" (project-BxZpbXj0V610b5Q6x1FV80gb). I first downloaded all the folders locally before running this script.
"""


parser = argparse.ArgumentParser(description=description,formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--sample-barcode-pairs",required=True,help="Tab-delimited text file with two column: 1) The sample name, and 2) The barcode for the sample. This information is needed to fill out the 'sample_name' field in the MISCE data transformation module.")
parser.add_argument("--data-processor-name",required=True,help="Full name of the person who did the analysis. This is used in the MISCE data transformation module for the column named 'data_processor_name'.")
parser.add_argument("--data-processor-institution",required=True,help="The institution at which the individual designated by --data-processor-name resides. This is used in the MISCE data transformation module for the column named 'data_processor_institution'.")
parser.add_argument("--project-name",required=True,help="The name of the lab's project. Corresponds to the column 'project_name' in the MISCE data transformation module.")
parser.add_argument("-o","--outfile",required=True,help="""Outfile name. The header line contains the following fields:
	- species_source_common_name
	- output_data
	- lab_snyder_genes_quant
	- lab_snyder_isoforms_quant
	- reference_data
	- data_processing_method_algorithm
	- data_processing_description
	- data_processing_software
	- data_processing_protocol_id
	- data_processor_name
	- data_processor_institution
	- project_name
	- sample_name
	- primary_data
	""")
args = parser.parse_args()
sample_barcode_pairs_file = args.sample_barcode_pairs
processor_name = args.data_processor_name
processor_institution = args.data_processor_institution
project_name = args.project_name
outfile = args.outfile

barcodes_file = open(sample_barcode_pairs_file)
barcodes = {}
line_count = 0
for line in barcodes_file:
	line_count += 1
	line = line.strip()
	if not line:
		continue
	sample,barcode = line.split("\t")
	if not sample:
		raise Exception("The file {} is missing a sample ID in row {}.".format(sample_barcode_pairs_file,row))
	if not barcode:
		raise Exception("The file {} is missing a barcode in row {}.".format(sample_barcode_pairs_file,row))
	barcodes[barcode] = sample	

fout = open(outfile,'w')

for d in os.listdir(PATIENTS_DIR):
	pat_dir = os.path.join(PATIENTS_DIR,d)
	if not os.path.isdir(pat_dir):
		continue
	#iterate through sample directories (barcodes) of each patient
	for s in os.listdir(pat_dir):
		barcode_dir = os.path.join(pat_dir,s)
		if not os.path.isdir(barcode_dir):
			continue
		gene_results_file = glob.glob(os.path.join(barcode_dir,"*.genes.results"))[0]
		gene_results_file = os.path.basename(gene_results_file)

		isoform_results_file = glob.glob(os.path.join(barcode_dir,"*.isoforms.results"))[0]
		isoform_results_file = os.path.basename(isoform_results_file)

		transcript_bam_file = glob.glob(os.path.join(barcode_dir,"*_anno.bam"))[0]
		transcript_bam_file = os.path.basename(transcript_bam_file)
	
		star_log = glob.glob(os.path.join(barcode_dir,"*_star_Log.final.out"))[0]
		star_log = os.path.basename(star_log)

		genomebam_plus_strand_bigwig = glob.glob(os.path.join(barcode_dir,"*_genome_plusAll.bw"))[0]
		genomebam_plus_strand_bigwig = os.path.basename(genomebam_plus_strand_bigwig)

		genomebam_minus_strand_bigwig = glob.glob(os.path.join(barcode_dir,"*_genome_minusAll.bw"))[0]
		genomebam_minus_strand_bigwig = os.path.basename(genomebam_minus_strand_bigwig)

		#Now the EBSeq output
		#Note that the control samples will have empty "ebseq" folders. 
	
		#EBSeq output (defunct)
#		try:
#			isoform_ebseq_res = glob.glob(os.path.join(barcode_dir,"ebseq","IsoMat_ebseq.results"))[0]
#			gene_ebseq_res = glob.glob(os.path.join(barcode_dir,"ebseq","GeneMat_ebseq.results"))[0]
#		except IndexError:
#			#a control barcode, which won't have EBSeq results in it's own ebseq folder. 
#			isoform_ebseq_res = ""
#			gene_ebseq_res = ""
		
		
		fastq_file_prefix = gene_results_file.split("R1_concat_")[0]
		r1_fastq_file = fastq_file_prefix + "R1.fastq.gz"
		r2_fastq_file = fastq_file_prefix + "R2.fastq.gz"
	
		fout.write("Homo sapiens\t") #species_source_common_name
		#now comes the analysis file columns:
		fout.write(transcript_bam_file + "\t") #lab_snyder_transcript_bam
		fout.write(star_log + "\t") #lab_snyder_star_log
		fout.write(genomebam_plus_strand_bigwig + "\t") #lab_snyder_genome_bam_plus_strand_bigwig
		fout.write(genomebam_minus_strand_bigwig + "\t") #lab_snyder_genome_bam_minus_strand_bigwig
		fout.write(gene_results_file + "\t") #lab_snyder_rsem_gene_results
		fout.write(isoform_results_file + "\t") #lab_snyder_rsem_isoform_results
		#fout.write(isoform_ebseq_res + "\t") #lab_snyder_ebseq_isoform
		#fout.write(gene_ebseq_res + "\t") #lab_snyder_ebseq_gene
		fout.write("hg19+ERCC92\t") #reference_data
		fout.write("STAR-RSEM\t")	#data_processing_method_algorithm
		fout.write("ENCODE Long RNA-Seq\t") #data_processing_description
		fout.write("STAR\t") #data_processing_software
		fout.write("RNA-Seq\t") #data_processing_protocol_id	
		fout.write(processor_name + "\t") #data_processor_name
		fout.write(processor_institution + "\t") #data_processor_institution 
		fout.write(project_name + "\t") #project_name
		fout.write(barcodes[os.path.basename(barcode_dir)] + "\t") #sample
		fout.write(r1_fastq_file + "," + r2_fastq_file + "\n") #primary_data; last column
		
fout.close()

#Questions:
# 1) version of software used?
# 2) README
# 3) why do we put "STAR" for data_processing_software?
# 4) why do we put RNA-Seq for data_processing_protocol_id?

