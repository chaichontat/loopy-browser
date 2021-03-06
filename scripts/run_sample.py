#%%
from pathlib import Path
from typing import Literal, cast

import numpy as np
import pandas as pd
from anndata import AnnData
from scanpy import read_visium
from tifffile import imread

from loopy.feature import ChunkedJSONParams, OverlayParams, PlainJSONParams, get_compressed_genes
from loopy.image import ImageParams, compress, gen_geotiff
from loopy.sample import Sample
from loopy.utils import Url

#%% [markdown]

# The directory contains spaceranger outputs.
# The out directory contains folders of processed images and features.
# These can be fed directly to "Add samples" in the Loopy Browser.

#%%

directory = Path("/Users/chaichontat/Documents/VIF")
out = Path("/Users/chaichontat/GitHub/loopy-browser/static")
samples = ["Br2720_Ant_IF", "Br6432_Ant_IF", "Br6522_Ant_IF", "Br8667_Post_IF"]

channels = [
    "Lipofuscin",
    "DAPI",
    "GFAP",
    "NeuN",
    "OLIG2",
    "TMEM119",
]


analyses = {
    "tsne": "analysis/tsne/2_components/projection.csv",
    "umap": "analysis/umap/2_components/projection.csv",
    "cluster_graph": "analysis/clustering/graphclust/clusters.csv",
    "kmeans2": "analysis/clustering/kmeans_2_clusters/clusters.csv",
    "kmeans3": "analysis/clustering/kmeans_3_clusters/clusters.csv",
    "kmeans4": "analysis/clustering/kmeans_4_clusters/clusters.csv",
    "kmeans5": "analysis/clustering/kmeans_5_clusters/clusters.csv",
    "kmeans6": "analysis/clustering/kmeans_6_clusters/clusters.csv",
    "kmeans7": "analysis/clustering/kmeans_7_clusters/clusters.csv",
    "kmeans8": "analysis/clustering/kmeans_8_clusters/clusters.csv",
    "kmeans9": "analysis/clustering/kmeans_9_clusters/clusters.csv",
    "kmeans10": "analysis/clustering/kmeans_10_clusters/clusters.csv",
}


def better_visium(d: Path, features: dict[str, str]) -> AnnData:
    """Need to include spaceranger analyses into the the AnnData object
    to make sure that the indices match."""
    vis = read_visium(d)
    for k, v in features.items():
        df = pd.read_csv(d / v, index_col=0)
        if len(df.columns) == 1:
            df.rename(columns={df.columns[0]: k}, inplace=True)
        else:
            df.rename(columns={c: f"{k}_{i}" for i, c in enumerate(df.columns, 1)}, inplace=True)
        vis.obs = vis.obs.join(df, how="left")
    return vis


def gen_coords(vis: AnnData, path: Path | str) -> None:
    spatial = cast(pd.DataFrame, vis.obsm["spatial"])
    coords = pd.DataFrame(
        spatial, columns=["x", "y"], index=pd.Series(vis.obs_names, name="id"), dtype="uint32"
    )
    return coords.to_csv(path)
    # return [CoordId(x=row.x, y=row.y, id=id_).dict() for id_, row in zip(vis.obs_names, coords.itertuples())]


def run(s: str) -> None:
    mPerPx = 0.497e-6
    sample = Sample(
        name=s,
        imgParams=ImageParams(
            urls=[Url(f"{s}_1.tif"), Url(f"{s}_2.tif")],
            channel=channels,
            mPerPx=mPerPx,
        ),
        overlayParams=[
            OverlayParams(
                name="spots", shape="circle", mPerPx=mPerPx, size=130e-6, url=Url("spotCoords.csv")
            ),
            # OverlayParams(name="cells", shape="circle", mPerPx=mPerPx, url=Url("cellCoords.csv")),
        ],
        featParams=[
            ChunkedJSONParams(
                name="genes", headerUrl=Url("gene_csc.json"), url=Url("gene_csc.bin"), overlay="spots"
            ),
            ChunkedJSONParams(
                name="spotGenes",
                headerUrl=Url("gene_csr.json"),
                url=Url("gene_csr.bin"),
                overlay=None,
            ),
            PlainJSONParams(name="umap", url=Url("umap.json"), dataType="coords", overlay="spots"),
            # PlainJSONParams(
            #     name="cellType", url=Url("cellType.json"), dataType="categorical", overlay="cells"
            # ),
            # PlainJSONParams(name="oligo", url=Url("oligo.json"), dataType="quantitative", overlay="spots"),
            # PlainJSONParams(name="Excit_A", url=Url("excita.json"), dataType="quantitative", overlay="spots"),
        ]
        + [
            PlainJSONParams(name=k, url=Url(k + ".json"), dataType="categorical", overlay="spots")
            for k in analyses
        ],
    )

    vis = better_visium(directory / s, features=analyses)
    vis.X.data = np.log2(vis.X.data + 1)  # type: ignore
    vis.var_names_make_unique()

    o = Path(out / s)
    o.mkdir(exist_ok=True, parents=True)
    (o / "sample.json").write_text(sample.json())

    for orient in ["csr", "csc"]:
        header, bytedict = get_compressed_genes(vis, cast(Literal["csc", "csr"], orient))
        (o / f"gene_{orient}.json").write_text(header.json().replace(" ", ""))
        (o / f"gene_{orient}.bin").write_bytes(bytedict)

    for k in analyses:
        if k in ["umap", "tsne"]:
            (o / f"{k}.json").write_text(
                vis.obs[[f"{k}_1", f"{k}_2"]]
                .rename(columns={f"{k}_1": "x", f"{k}_2": "y"})
                .to_json(orient="records", double_precision=3)
            )
        else:
            (o / f"{k}.json").write_text(vis.obs[k].to_json(orient="records", double_precision=3))

    gen_coords(vis, o / "spotCoords.csv")
    img = imread(directory / (s + ".tif"))
    tifs = gen_geotiff(img, o / s, mPerPx)
    compress(tifs)


for s in samples:
    run(s)

# %%
