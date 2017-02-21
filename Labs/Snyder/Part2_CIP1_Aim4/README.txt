2017-02-20
Nathaniel Watson
nathankw@stanford.edu


The ENCODE Long RNA-Seq workflow was run in the DNAnexus project project-BxZpbXj0V610b5Q6x1FV80gb (Joseph_Wu) for each of the 48 samples/barcodes. The command to run the analysis was:

python run_encode_rnaseq.py -g hg19 -t 6 -s project-F0bv6b00k49KxZvfGQG3v3qQ project-F0bxzXj0kgYq5Qzf9jp4fVB0 project-F0bz9GQ0FggyF151x0BQg678 project-F07jGX00P0By6yk2ZkFqVz06 project-F0bJ2bj05gbXG139J83jv49z project-F0b4Z3002Pf29FK60bqX7bg6  -w project-BxZpbXj0V610b5Q6x1FV80gb -b /srv/gsfs0/software/gbsc/cescg/Labs/Snyder/Part2_CIP1_Aim4/barcodes.txt

#There are 12 patients. Each was sequenced under the following 4 conditions:
	#iPSC
	#No Treatment
	#Prevastatin, 0.1 uM
	#Carvedilol, 0.1 uM

#For each patient, for each sample, I need to run the ENCODE Long RNA-Seq pipeline on hg19. Then, I'll need to run EBSeq (rsem-run-ebseq) to calculate both gene and isoform differential expression of each medicine dose
# against the 'No Treatment' sample. I can ignore the iPSC sample I'm told, but I'll go ahead and map it. 

#Each sample was sequenced 6 times. That is, the same barcode was sequenced in 6 lanes. They are the following 6 DNAnexus projects:
#	161111_GADGET_0079_AHFNKMBBXX_L1_SW03-11-02-16 (project-F0bv6b00k49KxZvfGQG3v3qQ)
#	161111_GADGET_0079_AHFNKMBBXX_L5_SW03-11-02-16 (project-F0bxzXj0kgYq5Qzf9jp4fVB0)
#	161111_GADGET_0079_AHFNKMBBXX_L6_SW03-11-02-16 (project-F0bz9GQ0FggyF151x0BQg678)
#	161020_COOPER_0067_BHFTW2BBXX_L5_SW03-ROY01 (project-F07jGX00P0By6yk2ZkFqVz06)
#	161108_COOPER_0071_AHFNKYBBXX_L1_SW03-11-02-16 (project-F0bJ2bj05gbXG139J83jv49z)
#	161107_GADGET_0078_BHFNKGBBXX_L5_SW03-11-02-16 (project-F0b4Z3002Pf29FK60bqX7bg6)

#When running the ENCODE pipeline, I'll run it for all 6 technical replicates at the same time.

#Note that for each of the FASTQ files in DNAnexus, I added three properties:
	#1) lab_patient_id
	#2) lab_patient_group
  #3) lab_patient_condition
#That way, I'll be able to easily query for the files that I need. Below I paste in the sample data that Eric Wei provided to me. 

#lab_patient_id	lab_patient_group	lab_patient_condition	Index
#287 #1A	HCM	iPSC	ATTACTCG-AGGCTATA
#287 #1B	HCM	No Treatment	ATTACTCG-GCCTCTAT
#287 #1C	HCM	Pravastatin 0.1 µM	ATTACTCG-AGGATAGG
#287 #1D	HCM	Carvedilol 0.1 µM	ATTACTCG-TCAGAGCC
#289 #1A	HCM	iPSC	ATTACTCG-CTTCGCCT
#289 #1B	HCM	No Treatment	ATTACTCG-TAAGATTA
#289 #1C	HCM	Pravastatin 0.1 µM	ATTACTCG-ACGTCCTG
#289 #1D	HCM	Carvedilol 0.1 µM	ATTACTCG-GTCAGTAC
#297 #1A	Control	iPSC	TCCGGAGA-AGGCTATA
#297 #1B	Control	No Treatment	TCCGGAGA-GCCTCTAT
#297 #1C	Control	Pravastatin 0.1 µM	TCCGGAGA-AGGATAGG
#297 #1D	Control	Carvedilol 0.1 µM	TCCGGAGA-TCAGAGCC
#304 #1A	LVNC (DCM)	iPSC	TCCGGAGA-CTTCGCCT
#304 #1B	LVNC (DCM)	No Treatment	TCCGGAGA-TAAGATTA
#304 #1C	LVNC (DCM)	Pravastatin 0.1 µM	TCCGGAGA-ACGTCCTG
#304 #1D	LVNC (DCM)	Carvedilol 0.1 µM	TCCGGAGA-GTCAGTAC
#320 #1A	DCM	iPSC	CGCTCATT-AGGCTATA
#320 #1B	DCM	No Treatment	CGCTCATT-GCCTCTAT
#320 #1C	DCM	Pravastatin 0.1 µM	CGCTCATT-AGGATAGG
#320 #1D	DCM	Carvedilol 0.1 µM	CGCTCATT-TCAGAGCC
#372 #1A	Control	iPSC	CGCTCATT-CTTCGCCT
#372 #1B	Control	No Treatment	CGCTCATT-TAAGATTA
#372 #1C	Control	Pravastatin 0.1 µM	CGCTCATT-ACGTCCTG
#372 #1D	Control	Carvedilol 0.1 µM	CGCTCATT-GTCAGTAC
#397 #1A	HCM	iPSC	GAGATTCC-AGGCTATA
#397 #1B	HCM	No Treatment	GAGATTCC-GCCTCTAT
#397 #1C	HCM	Pravastatin 0.1 µM	GAGATTCC-AGGATAGG
#397 #1D	HCM	Carvedilol 0.1 µM	GAGATTCC-TCAGAGCC
#284 #1A	Control	iPSC	GAGATTCC-CTTCGCCT
#284 #1B	Control	No Treatment	GAGATTCC-TAAGATTA
#284 #1C	Control	Pravastatin 0.1 µM	GAGATTCC-ACGTCCTG
#284 #1D	Control	Carvedilol 0.1 µM	GAGATTCC-GTCAGTAC
#310 #1A	HCM	iPSC	ATTCAGAA-AGGCTATA
#310 #1B	HCM	No Treatment	ATTCAGAA-GCCTCTAT
#310 #1C	HCM	Pravastatin 0.1 µM	ATTCAGAA-AGGATAGG
#310 #1D	HCM	Carvedilol 0.1 µM	ATTCAGAA-TCAGAGCC
#367 #1A	DCM	iPSC	ATTCAGAA-CTTCGCCT
#367 #1B	DCM	No Treatment	ATTCAGAA-TAAGATTA
#367 #1C	DCM	Pravastatin 0.1 µM	ATTCAGAA-ACGTCCTG
#367 #1D	DCM	Carvedilol 0.1 µM	ATTCAGAA-GTCAGTAC
#301 #1A	HCM	iPSC	GAATTCGT-AGGCTATA
#301 #1B	HCM	No Treatment	GAATTCGT-GCCTCTAT
#301 #1C	HCM	Pravastatin 0.1 µM	GAATTCGT-AGGATAGG
#301 #1D	HCM	Carvedilol 0.1 µM	GAATTCGT-TCAGAGCC
#352 #1A	HCM	iPSC	GAATTCGT-CTTCGCCT
#352 #1B	HCM	No Treatment	GAATTCGT-TAAGATTA
#352 #1C	HCM	Pravastatin 0.1 µM	GAATTCGT-ACGTCCTG
#352 #1D	HCM	Carvedilol 0.1 µM	GAATTCGT-GTCAGTAC

#I'll run the ENCODE Uniform Long RNA-Seq pipeline in the Joseph_Wu DNAnexus project (project-BxZpbXj0V610b5Q6x1FV80gb) and output the results in the same project and in the folder path Joseph_Wu/encode_long_rnaseq/part2_cip1_aim4. Within that folder, there will be a subfolder named after each patient ID, i.e. 287, and a sub-folder there-within named after the barcode. 
