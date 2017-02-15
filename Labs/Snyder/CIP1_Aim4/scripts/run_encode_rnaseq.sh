#!/bin/bash -eu
set -o pipefail

#make sure the following environment modules are loaded:
## 1) gbsc/dnanexus/current

source $DXTOOLKIT

log_into_dnanexus.sh -u nathankw

lane1_fastqs=$(dx ls --brief project-BxZpbXj0V610b5Q6x1FV80gb:/160510_COOPER_0034_BH7K2MBBXX_L1/stage0_bcl2fastq/fastqs)
lane1_fastqs=(${lane1_fastqs}) #convert to array

lane5_fastqs=$(dx ls --brief project-BxZpbXj0V610b5Q6x1FV80gb:/160510_COOPER_0034_BH7K2MBBXX_L5/stage0_bcl2fastq/fastqs)
lane5_fastqs=(${lane5_fastqs}) #convert to array

#There are 5 patients. Each patient was barcoded, and given 3 two treatments of medicine (different doses) and one control (no medicine). Each of the patients was sequenced in replicate on two lanes of a HiSeq 4000 - lanes 1 and 5. The goal is to run the ENCODE long RNA-Seq pipeline on each treatment and control condition for each patient. Each time I run the pipeline, I will specify the replicates - two forward read files and two reverse read files.

#The following table is part of the metadata that was provided and is stored in the DNAnexus project named Joseph_Wu (project-BxZpbXj0V610b5Q6x1FV80gb).
#Sample	Group	Condition	Index 
#287 #1a	HCM	No Treatment	ATTACTCG-AGGCTATA
#287 #1b	HCM	Pravastatin 0.1 µM	ATTACTCG-GCCTCTAT
#287 #1c	HCM	Pravastatin 1 µM	ATTACTCG-AGGATAGG
#289 #1a	HCM	No Treatment	ATTACTCG-TAAGATTA
#289 #1b	HCM	Pravastatin 0.1 µM	ATTACTCG-ACGTCCTG
#289 #1c	HCM	Pravastatin 1 µM	ATTACTCG-GTCAGTAC
#295 #1a	HCM	No Treatment	TCCGGAGA-AGGATAGG
#295 #1b	HCM	Pravastatin 0.1 µM	TCCGGAGA-TCAGAGCC
#295 #1c	HCM	Pravastatin 1 µM	TCCGGAGA-CTTCGCCT
#297 #1a	Control	No Treatment	TCCGGAGA-TAAGATTA
#297 #1b	Control	Pravastatin 0.1 µM	TCCGGAGA-ACGTCCTG
#297 #1c	Control	Pravastatin 1 µM	TCCGGAGA-GTCAGTAC
#301 #1a	Control	No Treatment	CGCTCATT-AGGCTATA
#301 #1b	Control	Pravastatin 0.1 µM	CGCTCATT-GCCTCTAT
#301 #1c	Control	Pravastatin 1 µM	CGCTCATT-AGGATAGG

for i in lane1_fastqs
do
	
