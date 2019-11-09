# Extract tissue and cell-type signatures from FANTOM5 gene expression data

## Input Data
* We obtained gene expression data and the FANTOM5 ontology from the [FANTOM5 project, phase 2.2](http://fantom.gsc.riken.jp/5/datafiles/phase2.2/). 
* We obtained additional sample annotation from the supplementary table S1 from the [FANTOM5 publication](https://doi.org/10.1038/nature13182)

## Reconciling the sample annotation
There are three sources for sample annotations:
1. **The sample name,** e.g. `tpm of 293SLAM rinderpest infection, 00hr, biol_rep1.CNhs14406.13541-145H4`,
contain the library id `CNhs14406` which is unique for each sample,
a sample description (`293SLAM rinderpest infection`),
an accession number `13541-145H4` and
addition covariates (e.g. `00hr`, `biol_repl`) that are relevant for the analysis.
2. **The FANTOM5 ontology** is provided as an obo-file and linked to the accession number of each sample. 
3. **The table S1**. 

Unfortunately, the three sources are to some extend inconsistent and some information available in one source is lacking in another. We, therefore, attempt to reconcile the three sources to obtain an as-accurate-as-possible sample annotation. 

* The jupyter notebook used to reconcile the annotations can be found here: [01_process_sample_annotation.ipynb](notebooks/01_process_sample_annotation.ipynb)
* The python module that implements the stragety for merging entries is here: [parse_ontoloby.py](pyfantom/parse_ontology.py)
* The final, improved annotation is here: [column_vars.processed.csv](data/column_vars.processed.csv). 

## Generating signatures
To generate gene signatures from the samples, we developed the [pygenesig](https://github.com/grst/pygenesig) package. 

* We prepare the gene expression data and sample annotations from FANTOM5 for the use with pygenesig: [07_prepare_data_for_pygenesig.ipynb](notebooks/07_prepare_data_for_pygenesig.ipynb). 
* We generate signatures and perform two-fold cross-validation. We exclude signatures that don't meet our sensitivity and specificity criteria: [08_signature_corssvalidation](notebooks/08_signature_crossvalidation.ipynb). 

## Final signatures
The final signatures are available as gmt file: 
* TODO
* TODO 
