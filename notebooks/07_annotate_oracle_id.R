library(ribiosAnnotation)
library(readr)
library(assertthat)

fdata = read_csv("../data/pygenesig/by_gene_sum/fdata.csv")
annot = annotateGeneIDs(fdata$ora_id)
assert_that(nrow(annot) == nrow(fdata))
assert_that(all(fdata$ora_id == annot$GeneID))
write_tsv(annot['GeneSymbol'], "../data/pygenesig/by_gene_sum/gene_symbols.csv", col_names=FALSE)
