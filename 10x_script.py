#!/usr/bin/env python3

# import necessary packages
import scanpy as sc
import sys
import os

cwd = os.getcwd()
sc.settings.verbosity = 3             # verbosity: errors (0), warnings (1), info (2), hints (3)
sc.logging.print_header()
sc.settings.set_figure_params(dpi=80, facecolor='white')

n = len(sys.argv)      # number of arguments given
if n != 3:
    print("Enter only 1 input .h5 file:", n)  # return if no input file is given
else:
    adata = sc.read_10x_h5(sys.argv[1])                      # read `.h5` file
    adata.var_names_make_unique()                            # make variable names unique
    sc.pp.filter_cells(adata, min_counts=500)                # filter out cells with less than 500 counts
    sc.pp.filter_cells(adata, max_genes=6000)                # filter out cells with more than 6000 genes
    sc.pp.filter_genes(adata, min_cells=0.05*adata.n_obs)    # keep genes expressed in atleast 5% of cells
    adata.var['mt'] = adata.var_names.str.startswith('MT-')  # annotate the group of mitochondrial genes as 'mt'
    sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], percent_top=None, log1p=False, inplace=True)  # calculate the qc metrics for mitochondrial genes
    adata = adata[adata.obs.pct_counts_mt < 10, :]           # less than 10% mitochondrial genes
    sc.pp.normalize_total(adata, target_sum=1e5)             # total normalize with 100,000 reads per cell
    sc.pp.log1p(adata)                                       # log normalize the data
    sc.pp.highly_variable_genes(adata,n_top_genes=2000)      # select top 2000 highly variable genes.
    adata.raw = adata                                        # save the raw data for further analysis
    result_file = sys.argv[2]                                # the file that will store the analysis results
    adata.write(result_file+'.h5ad')                         # write the count matrix in .h5ad
    sc.pp.regress_out(adata, ['total_counts', 'pct_counts_mt']) # regress out effects of total counts per cell and the percentage of mitochondrial genes expressed
    sc.pp.scale(adata, max_value=10)                         # Scale each gene to unit variance. Clip values exceeding standard deviation 10.
    sc.tl.pca(adata,n_comps=50)                              # PCA embedding with 50 PCs.
    sc.pp.neighbors(adata, n_neighbors=100, n_pcs=50)        # nearest neighborhood graph of 100 neighbors from the 50 PCs
    sc.tl.umap(adata)                                        # embedding umap
    sc.tl.leiden(adata, resolution=1.3)                      # leiden clustering on PCA embedding with resolution 1.3
    sc.pl.umap(adata, color='leiden', save=".png")           # plot and save umap graph with leiden labels
    sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon') # leiden cluster using Mann-Whitney-U test,
    sc.pl.rank_genes_groups(adata, n_genes=25, save=".png")     # save gene rank plot
    os.rename(cwd+"/figures/umap.png",result_file+"_umap.png")   # the plots are saved in a directory by default and hence move it for it to be recognised as output
    os.rename(cwd+"/figures/rank_genes_groups_leiden.png",result_file+"_rank_genes_groups_leiden.png")

