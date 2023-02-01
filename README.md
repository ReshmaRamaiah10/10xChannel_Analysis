# WDL workflow to analyze gene counts

The 10xChannel_Analysis repository provided a WDL workflow to analyze gene-count matrices of human single-cell data using SCANPY.

## Pipeline Overview ##

The pipeline is built on a python script that analyzes a data file saved in the Hierarchical Data Format (H5 files) using scanpy ([tutorial](https://scanpy-tutorials.readthedocs.io/en/latest/pbmc3k.html)). It filters out unnecessary cells and genes to cluster the dataset and find marker genes.

The following steps are included in the analysis:
1. Filter out cells with less than 500 counts and more than 6000 genes.
2. Keep genes expressed in at least 5% of cells.
3. Since mitochondria are larger than individual transcript molecule, keep the cells with less than 10% mitochondrial genes.
4. Log normalize the data matrix to 100,000 reads per cell, so that counts become comparable among cells.
5. Identify highly-variable genes and keep the top 2000.
6. Regress out the effects of total counts per cell and the percentage of mitochondrial genes expressed. 
7. Scale each gene to one unit variance. Clip values exceeding standard deviation 10.
8. Reduce the dimensionality of the data by running principal component analysis (PCA) with 50 PCs, which reveals the main axes of variation and denoises the data.
9. Compute the neighborhood graph of cells using the PCA representation of the data matrix with 50 PCs.
10. Clustering the neighborhood graph using the Leiden graph-clustering method with resolution 1.3
11. Embed the graph in two dimensions using UMAP and generate an UMAP plot with cells colored by their leiden labels.
12. Find marker genes for each leiden cluster using the Mann-Whitney-U test, and generate the gene rank plot.

A docker image is built and run on a linux/amd64 platform with all the necessary packages like Python-3.9.15, scanpy, and leidenalg.
`docker build --platform linux/amd64 -t reshmaramaiah/10x_analysis:scanpy .`
`docker run --platform linux/amd64 reshmaramaiah/10x_analysis:scanpy`

A WDL workflow was developed using the Docker image to analyze multiple input files at once. It runs the Python script each time for every input file to generate the output files. [WOmtool](https://github.com/broadinstitute/cromwell/releases) was used to check the syntax of your WDL workflow:
`java -jar womtool-84.jar validate 10xchannel.wdl`
The pipeline was run on the WDL workflow engine [Cromwell](https://github.com/broadinstitute/cromwell/releases) along with an input json file:
`java -jar cromwell-84.jar run 10xchannel.wdl -i inputs.json`
inputs.json:
`{"Analysis.inputfiles":["raw_feature_bc_matrix1.h5","raw_feature_bc_matrix2.h5","raw_feature_bc_matrix3.h5","raw_feature_bc_matrix4.h5","raw_feature_bc_matrix5.h5","raw_feature_bc_matrix6.h5","raw_feature_bc_matrix7.h5","raw_feature_bc_matrix8.h5"]}`
Cromwell requires a [Java](https://www.oracle.com/java/technologies/javase/jdk13-archive-downloads.html) environment, of which version 13 was used.

### Pipeline input ###
| Name | Type | Description |
| --- | --- | --- |
| inputfiles | `Array[File]` | Array for H5 files to be analysed (sep = ",") |

### Pipeline output ###
| Name | Type | Description |
| --- | --- | --- |
| count_matrix_h5ad | `Array[File]` | The count matrix in h5ad format containing filtered cells and clustering results. It's a list since each channel should return one such file |
| umap_png | `Array[File]` | The UMAP plot of each channel |
| gene_rank_png | `Array[File]` | The gene rank plot of each channel |

Since scanpy creates a new folder to save the figures, the plots are moved to the execution folder in the python script for them to be identified as outputs by the workflow.

8 10x channels obtained from bone marrow cells were analyzed using the pipeline, and the plots are uploaded on this repository.
