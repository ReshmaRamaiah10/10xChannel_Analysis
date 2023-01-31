version 1.0

workflow Analysis {
    input {
        Array[File] inputfiles
          }
    call Channel {
        input:
            inputfiles = inputfiles
          }         
    output {
        Array[File] count_matrix_h5ad = Channel.count_matrix_h5ad
        Array[File] umap_png = Channel.umap_png
        Array[File] gene_rank_png = Channel.gene_rank_png
        }
}

task Channel {
    input {
        Array[File] inputfiles
          }
    command {
        set -exo pipefail
        for file in ~{sep=',' inputfiles}
            do
                python /usr/local/src/10x_script.py $file $(basename $file .h5)
            done;
        
          }
    output {
        Array[File] count_matrix_h5ad = glob("*.h5ad")
        Array[File] umap_png = glob("*umap.png")
        Array[File] gene_rank_png = glob("*rank_genes_groups_leiden.png")
          }
    runtime {
        docker: "reshmaramaiah/10x_analysis"
          }
}