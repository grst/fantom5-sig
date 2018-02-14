# Extract cell specific gene signatures from FANTOM5 gene expression data

## 1. Preprocessing
In the first step, we load the whole FANTOM5 expression matrix into a R/Bioconductor ExpressionSet.
The expression matrix is a huge, ca. 200000x1800 table. The column names,
e.g. `tpm of 293SLAM rinderpest infection, 00hr, biol_rep1.CNhs14406.13541-145H4`
contain the library id `CNhs14406` which is unique for each sample, an accession number `13541-145H4` and
addition covariates (e.g. `00hr`) that are relevant for the analysis.

Since the examples names are not consistently annotated, we use the
[ontology provided by FANTOM5](http://fantom.gsc.riken.jp/5/datafiles/latest/extra/Ontology/ff-phase2-140729.obo.txt)
to extract the information. Additionally, we check, if the annotation from the ontology
is consistent with the annotation in the sample name.
This process is documented in [`process_headers.ipynb`](process_headers.ipynb).

We discover in `explorer_ontology.ipynb` that the ontology also comes with some caveats, namely
* there are inconsistencies in the annotation of the sample type (i.e. primary cell vs. cell line vs. tissue)
* a siginificant amount of samples appears as singletons in the network,
i.e. they are not grouped according to replicates and tissue of origin.

Based on these findings, we attempt to adress these problems in `improve_ontology.ipynb`.

### Converting to R Expression set
We then read the matrix and the column annotation into an R Expression Object.
This process is documented in [`load_f5.Rmd`](load_f5.Rmd).

## Results
The improved annotation file is found in
```
data/column_vars.processed.csv
```

