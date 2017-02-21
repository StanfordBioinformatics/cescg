2015-10-20
Nathaniel Watson

StanfordFilenameConversion.txt is a file from Alex Pollen, where it contains a column for the current FASTQ file name and a column for the new FASTQ file name, as well as some extraneous columns.

I created oldName_newName.txt from StanfordFilenameConversion.txt using the command:
	cut -f1,6 StanfordFilenameConversion.txt  > oldName_newName.txt
in order that I only have the old name column and new name column side-by-side and in that order.

Next, I added a new name for the unmatched read files as well. Each lane has one unmatched read file for the forward read and one for the reverse read.
Alex didn't have a new named set for them, so I created them, using is naming convention by prefixing the library name (but the the combination of library_name and well_number since we don't have a well_number for 
the unmatched reads). For example, I renamed the file 150722_MARPLE_0320_BC7DL4ACXX_L8_unmatched_1_pf.fastq.gz from sequencing library S73 to  S73_150722_MARPLE_0320_BC7DL4ACXX_L8_unmatched_1_pf.fastq.gz.





