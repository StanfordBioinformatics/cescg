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


