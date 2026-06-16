import stream
import scanpy
import pandas
import numpy
import anndata as ad
import rpy2.robjects as robjects  # interface python-R

adata = ad.read_h5ad("/workspace/data/M_E10_sn_res0.5.h5ad")

stream.set_workdir(
    adata,
    "/workspace/data/M_E10_sn_res0.5_hd5f_result"
)

adata.obsm["X_dr"] = adata.obsm["X_umap_var"]
adata.obsm["X_vis_umap"] = adata.obsm["X_umap_var"]

stream.add_metadata(
    adata,
    file_name="M_E10_sn_res0.5_Dphpal_metadata.csv",
    file_path="/workspace/data",
    delimiter=",",
)

stream.plot_dimension_reduction(
    adata,
    color=["label"],
    n_components=2,
    show_graph=False,
    show_text=False,
    fig_ncol=1,
    fig_legend_ncol=1,
    save_fig=True,
    fig_name="Fig1.pdf",
)

# My selection: n_cluster = 10 and epg_mu = 0.05
stream.seed_elastic_principal_graph(adata, n_clusters=10)

stream.plot_dimension_reduction(
    adata,
    color=["label", "kmeans", "branch_id"],
    n_components=2,
    show_graph=True,
    fig_ncol=3,
    fig_legend_ncol=1,
    save_fig=True,
    fig_name="M_E10_sn_res0.5_kmeans_10clusters_epgmu005.pdf",
)

# Elastic Principal Graph
stream.elastic_principal_graph(
    adata,
    epg_alpha=0.02,
    epg_mu=0.05,
    epg_lambda=0.03,
    fig_name="ElPiGraph_epgmu005.pdf",
)

stream.plot_dimension_reduction(
    adata,
    color=["kmeans", "label", "Phase"],
    n_components=2,
    show_graph=True,
    fig_ncol=1,
    fig_legend_ncol=1,
    save_fig=True,
    fig_name="final_selection.pdf",
)

stream.plot_flat_tree(
    adata,
    color=["label"],
    show_graph=True,
    show_text=True,
    dist_scale=0.5,
    fig_ncol=1,
    fig_legend_ncol=1,
    save_fig=True,
    fig_name="final_selection_flat_tree.pdf",
)

stream.plot_stream(
    adata,
    root="S1",
    color=["kmeans", "label", "Phase"],
    dist_scale=3,
    fig_legend_ncol=1,
    save_fig=True,
    fig_path="/workspace/data/M_E10_sn_res0.5_hd5f_result/final_selection_stream",
)

stream.write(
    adata,
    file_name="M_E10_sn_UmapSeurat_ncl10_epgmu0.05_adata.pkl"
)