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

Signature genes are selected using a stragegy based on gini-information gain we described in the [BioQC publication](https://bmcgenomics.biomedcentral.com/articles/10.1186/s12864-017-3661-2).
In brief, the method calculates Gini-index to identify genes with a high information gain, according to the following steps:

1. Aggregate samples of the same tissue or cell-type by their median gene expression, resulting in a `genes` x `cell-type` matrix `X`.
2. Compute gini index on that matrix, resulting in a vector `g` of length `genes`.
3. Compute the ranks of the gene expression `X` for each gene across all cell-types, resulting in another `genes` x `cell-types` matrix `R`.
4. Compute the quantiles of the gene expression `X` for each gene across each sample, resulting in another `genes` x `cell-types` matrix `Q`.
5. For each gene `i` and cell-type `j`, include a gene into the signature, if (1) `g(i) >= 0.7` and (2) `R(i, j) <= 3` and (3) `X(i, j) >= 1 TPM` and (4) `Q(i, j) > 0.66`. In other words, this means that the gene needs to be (1+2) highly specific to the cell-type, (3) robustly expressed (4) among the top 33% of highest expressed genes in the respective cell-type.

For primary cells signatures, we differntiate between *fine* and *coarse* signatures. 
For the *coarse* signatures, we grouped primary cells of the same type, but different tissue origin into a single signature. For instance, breast, omental, perirenal and subcutaneous adipocytes were grouped into `adipocytes`. 


## Final signatures
The final signatures are available as gmt file:
* [Primary cell fine](gmt/exp.fantom5.primary_cells_HQ.roche.symbol.gmt)
* [Primary cell coarse](gmt/exp.fantom5.primary_cell_coarse.grst.symbol.gmt)
* [Tissues](gmt/exp.fantom5.tissue.grst.symbol.gmt)
