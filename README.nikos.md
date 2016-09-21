 human_samples_nature13182-s2.txt --> table supplied by the publication

   ---> CNhs1234 numbers
 human_samples_nature13182-s2_LIBRARY_IDs
This is just a tablem no actual data

--------------------------------------------
Tha data we are dealing with:

		from Kephar    ->   data file    (http://fantom.gsc.riken.jp/5/datafiles/latest/extra/CAGE_peaks/)--->
comment fron the  00_readme.txt in the above site:			
hg19.cage_peak_phase1and2combined_tpm_ann.osc.txt.gz - CAGE peak based expression table (RLE normalized) for human with annotation

		
	hg19.cage_peak_phase1and2combined_tpm_ann.osc.txt
The "real data" (numbers) start at the 8th column of hg19.cage_peak_phase1and2combined_tpm_ann.osc.txt from line 1840 onwards
This line starts with :chr10:100013403..100013414,
There are 7 columns with various info and from (and including) the 8th onwards 1836-7=1829 columns with the "real data".
The header of each of these columns are  in the line   1838 which starts as:
00Annotation    short_description       description     association_with_transcript     entrezgene_id   hgnc_id uniprot_id      tpm.293SLAM%20rinderpest%20infection%2c%2000hr%2c%20biol_rep1.CNhs14406.13541-145H4 etc

e.g., tpm.293SLAM%20rinderpest%20infection%2c%2000hr%2c%20biol_rep1.CNhs14406.13541-145H4
is the header of the first "real data" column
-----
HOW TO GET ALL THE HEADERS --> 
head -1838 hg19.cage_peak_phase1and2combined_tpm_ann.osc.txt | tail -1 > ALL_HEADERS
-----


awk -v FS="\t" '{print $6}' human_samples_nature13182-s2 > human_samples_nature13182-s2_LIBRARY_IDs
wcl samples1829_LIBRARY_IDs
    1829

awk '{split($0,a,".CNhs");split(a[2],b,".");print "CNhs"b[1]}' samples1829 > samples1829_LIBRARY_IDs
wcl human_samples_nature13182-s2_LIBRARY_IDs
988 						  
   
    All the 988 LIBRARY_IDs from human_samples_nature13182-s2 (from publication website) are included in the 1829 LIBRARY_IDs of samples1829_LIBRARY_IDs (from Kephar)
---------------------->
...........>
Making sense out of the headers...
the first column (a number) shows the 1-based order of the column, where the 1st coilumn starts at the 8th col of the data file (the fitst 7 havinf coord info, etc).
Example, the sample with numebr 123 (123rd) line correspond to the 130th column in the data file.

awk -v FS="\t" '{split($0,a,"=");m=split(a[2],b,",");split(b[m],c,".CNhs");s=NR;for(i=1;i<m;i++)s=s"\t"b[i];print s"\t"c[1]"\tCNhs."c[2]}' samples1829 | sed -e 's/tpm of //g' > samples1829_simplified

or equivalently
awk -v FS="\t" '{split($0,a,"=");split(a[2],b,".CNhs");m=split(b[1],c,",");s=NR;for(i=1;i<=m;i++)s=s"\t"c[i];print s"\tCNhs."b[2]}' samples1829 | sed -e 's/tpm of //g'
-------------->

Here are all the samples that include the word "monocyte"
 cut -f2 samples1829_simplified | sort | uniq -c | grep -i monocyte

  Here are all the different samples. The number in the front is the number of data columns for each one of them (multiple donors and/or multiple timepoints)
For example, the first sample below has data from 3 donors and 26 timepoints, but for the last timepoint thre are data only from 2 of the donors, 
e.g., 3*25 + 1*2 = 77 totally

cut -f2 samples1829_simplified | sort | uniq -c | sort -nr
     77 Monocyte-derived macrophages response to LPS
     62 ARPE-19 EMT induced with TGF-beta and TNF-alpha
     54 Saos-2 osteosarcoma treated with ascorbic acid and BGP to induce calcification
     54 mesenchymal stem cells (adipose derived)
     54 K562 erythroblastic leukemia response to hemin
     53 Myoblast differentiation to myotubes
     48 MCF7 breast cancer cell line response to EGF1
     48 Lymphatic Endothelial cells response to VEGFC
     48 iPS differentiation to neuron
     45 MCF7 breast cancer cell line response to HRG
     44 H9 Embryoid body cells
     39 HES3-GFP Embryonic Stem cells
     30 Aortic smooth muscle cell response to IL1b
     30 Aortic smooth muscle cell response to FGF2
     16 Monocyte-derived macrophages response to udorn influenza infection
     15 COBL-a rinderpest infection
     13 Fibroblast - Gingival
     12 COBL-a rinderpest(-C) infection
     12 Adipocyte differentiation
     12 293SLAM rinderpest infection
     10 Smooth muscle cells - airway
      9 H1 embryonic stem cells differentiation to CD34+ HSC
      8 Whole blood (ribopure)
      8 Monocyte-derived macrophages response to mock influenza infection
      8 Mast cell
      8 CD8+ T Cells (pluriselect)
      8 CD19+ B Cells (pluriselect)
      7 Bronchial Epithelial Cell
      6 Smooth Muscle Cells - Aortic
      6 Skeletal Muscle Cells
      6 Fibroblast - Periodontal Ligament
      6 Fibroblast - Dermal
      6 Fibroblast - Cardiac
      5 putamen
      5 mesenchymal precursor cell - ovarian cancer right ovary
      5 Fibroblast - skin spinal muscular atrophy
      5 Fibroblast - skin dystrophia myotonica
      5 Fibroblast - Aortic Adventitial
      4 thalamus
      4 spinal cord
      4 Small Airway Epithelial Cells
      4 Retinal Pigment Epithelial Cells
      4 Renal Glomerular Endothelial Cells
      4 parietal lobe
      4 Olfactory epithelial cells
      4 Mesenchymal Stem Cells - bone marrow
      4 mesenchymal precursor cell - ovarian cancer metastasis
      4 mesenchymal precursor cell - ovarian cancer left ovary
      4 mesenchymal precursor cell - cardiac
      4 medial temporal gyrus
      4 mature adipocyte
      4 heart
      4 Fibroblast - skin normal
      4 Endothelial Cells - Aortic
      4 Dendritic Cells - monocyte immature derived
      4 adipose
      3 Urothelial Cells
      3 Tracheal Epithelial Cells
      3 Trabecular Meshwork Cells
      3 tenocyte
      3 temporal lobe
      3 Synoviocyte
      3 substantia nigra
      3 Smooth Muscle Cells - Umbilical Vein
      3 Smooth Muscle Cells - Umbilical Artery
      3 Smooth Muscle Cells - Tracheal
      3 Smooth Muscle Cells - Subclavian Artery
      3 Smooth Muscle Cells - Pulmonary Artery
      3 Smooth Muscle Cells - Prostate
      3 Smooth Muscle Cells - Internal Thoracic Artery
      3 Smooth Muscle Cells - Coronary Artery
      3 Smooth Muscle Cells - Colonic
      3 Smooth Muscle Cells - Carotid
      3 Smooth Muscle Cells - Brain Vascular
      3 Smooth Muscle Cells - Brachiocephalic
      3 Skeletal Muscle Satellite Cells
      3 Skeletal muscle cells differentiated into Myotubes - multinucleated
      3 Sebocyte
      3 Schwann Cells
      3 Saos-2 osteosarcoma cell line
      3 salivary acinar cells
      3 Renal Proximal Tubular Epithelial Cell
      3 Renal Mesangial Cells
      3 Renal Epithelial Cells
      3 Prostate Stromal Cells
      3 promyelocytes/myelocytes PMC
      3 Preadipocyte - visceral
      3 Preadipocyte - subcutaneous
      3 Preadipocyte - omental
      3 Preadipocyte - breast
      3 Placental Epithelial Cells
      3 Peripheral Blood Mononuclear Cells
      3 Pericytes
      3 Osteoblast - differentiated
      3 Osteoblast
      3 Nucleus Pulposus Cell
      3 Neutrophils
      3 neutrophil PMN
      3 Neurons
      3 Natural Killer Cells
      3 nasal epithelial cells
      3 Myoblast
      3 migratory langerhans cells
      3 Mesothelial Cells
      3 Mesenchymal Stem Cells - umbilical
      3 Mesenchymal Stem Cells - adipose
      3 mesenchymal precursor cell - bone marrow
      3 mesenchymal precursor cell - adipose
      3 Meningeal Cells
      3 Melanocyte - light
      3 Melanocyte - dark
      3 Melanocyte
      3 medulla oblongata
      3 medial frontal gyrus
      3 Mammary Epithelial Cell
      3 Mallassez-derived cells
      3 Macrophage - monocyte derived
      3 lung
      3 locus coeruleus
      3 Lens Epithelial Cells
      3 Keratocytes
      3 Keratinocyte - epidermal
      3 hIPS +CCl2
      3 hIPS
      3 hippocampus
      3 Hepatocyte
      3 hepatocellular carcinoma cell line: HepG2 ENCODE
      3 Hepatic Stellate Cells (lipocyte)
      3 Hepatic Sinusoidal Endothelial Cells
      3 Hep-2 cells treated with Streptococci strain JRS4
     3 Hep-2 cells treated with Streptococci strain 5448
      3 Hep-2 cells mock treated
      3 Hair Follicle Dermal Papilla Cells
      3 H9 Embryonic Stem cells
      3 granulocyte macrophage progenitor
      3 globus pallidus
      3 Gingival epithelial cells
      3 Fibroblast - Villous Mesenchymal
      3 Fibroblast - Mammary
      3 Fibroblast - Lymphatic
      3 Fibroblast - Lung
      3 Fibroblast - Choroid Plexus
      3 Esophageal Epithelial Cells
      3 epitheloid carcinoma cell line: HelaS3 ENCODE
      3 Eosinophils
      3 Endothelial Cells - Vein
      3 Endothelial Cells - Umbilical vein
      3 Endothelial Cells - Microvascular
      3 Endothelial Cells - Lymphatic
      3 Endothelial Cells - Artery
      3 Dendritic Cells - plasmacytoid
      3 Corneal Epithelial Cells
      3 colon
      3 Ciliary Epithelial Cells
      3 chronic myelogenous leukemia cell line:K562 ENCODE
      3 chorionic membrane cells
      3 Chondrocyte - de diff
      3 cerebellum
      3 CD8+ T Cells
      3 CD4+ T Cells
      3 CD4+CD25+CD45RA+ naive regulatory T cells expanded
      3 CD4+CD25+CD45RA+ naive regulatory T cells
      3 CD4+CD25-CD45RA+ naive conventional T cells expanded
      3 CD4+CD25-CD45RA+ naive conventional T cells
      3 CD4+CD25+CD45RA- memory regulatory T cells expanded
      3 CD4+CD25+CD45RA- memory regulatory T cells
      3 CD4+CD25-CD45RA- memory conventional T cells expanded
      3 CD4+CD25-CD45RA- memory conventional T cells
      3 CD19+ B Cells
      3 CD14+ monocytes - treated with Trehalose dimycolate (TDM)
      3 CD14+ monocytes - treated with Salmonella
      3 CD14+ monocytes - treated with lipopolysaccharide
      3 CD14+ monocytes - treated with IFN + N-hexane
      3 CD14+ monocytes - treated with Group A streptococci
      3 CD14+ monocytes - treated with Cryptococcus
      3 CD14+ monocytes - treated with Candida
      3 CD14+ monocytes - treated with B-glucan
      3 CD14+ monocytes - treated with BCG
      3 CD14+ monocytes - mock treated
      3 CD14+ Monocytes
      3 CD14+ monocyte derived endothelial progenitor cells
      3 CD14+CD16+ Monocytes
      3 CD14+CD16- Monocytes
      3 CD14-CD16+ Monocytes
      3 caudate nucleus
      3 Cardiac Myocyte
      3 brain
      3 B lymphoblastoid cell line: GM12878 ENCODE
      3 Basophils
      3 Astrocyte - cerebral cortex
      3 Astrocyte - cerebellum
      3 amniotic membrane cells
      3 Amniotic Epithelial Cells
      3 Alveolar Epithelial Cells
      3 Adipocyte - subcutaneous
      3 Adipocyte - omental
      2 uterus
      2 trachea
      2 tongue
      2 thyroid
      2 thymus
      2 throat
      2 testis
      2 spleen
      2 Smooth Muscle Cells - Uterine
      2 Smooth Muscle Cells - Esophageal
      2 Smooth Muscle Cells - Bronchial
      2 small intestine
      2 skin
      2 skeletal muscle
      2 Sertoli Cells
      2 schwannoma cell line:HS-PSS
      2 Renal Cortical Epithelial Cells
      2 Prostate Epithelial Cells
      2 pituitary gland
      2 pineal gland
      2 Perineurial Cells
      2 occipital lobe
      2 occipital cortex
      2 Neural stem cells
      2 Multipotent Cord Blood Unrestricted Somatic Stem Cells
      2 mesothelioma cell line:Mero-14
      2 Mesenchymal Stem Cells - hepatic
      2 Mesenchymal Stem Cells - amniotic membrane
      2 liver
      2 kidney
      2 immature langerhans cells
      2 Hair Follicle Outer Root Sheath Cells
      2 glioblastoma cell line:A172
      2 gamma delta positive T cells
      2 Fibroblast - skin
      2 Fibroblast - Conjunctival
      2 Endothelial Cells - Thoracic
      2 duodenum
      2 common myeloid progenitor CMP
      2 Chondrocyte - re diff
      2 CD34+ stem cells - adult bone marrow derived
      2 CD34+ Progenitors
      2 CD34 cells differentiated to erythrocyte lineage
      2 Anulus Pulposus Cell
      2 amygdala
      2 Adipocyte - breast
      1 xeroderma pigentosum b cell line:XPL 17
      1 Wilms' tumor cell line:HFWT
      1 Wilms' tumor cell line:G-401
      1 vein
      1 vagina
      1 Urothelial cells
      1 Urethra
      1 Universal RNA - Human Normal Tissues Biochain
      1 umbilical cord
      1 tubular adenocarcinoma cell line:SUIT-2
      1 tridermal teratoma cell line:HGRT
      1 transitional-cell carcinoma cell line:JMSU1
      1 transitional cell carcinoma cell line:Hs 769.T
      1 transitional-cell carcinoma cell line:5637
      1 tonsil
      1 tongue epidermis (fungiform papillae)
      etc.