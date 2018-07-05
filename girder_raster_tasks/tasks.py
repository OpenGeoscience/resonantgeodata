from functools import partial
import os
import tempfile
import pyproj
import rasterio
from rasterio.tools.mask import mask
from shapely.ops import transform
from girder_worker.app import app
from girder_worker.utils import girder_job
from shapely.geometry import shape, mapping


def reprojectGeometry(geometry, projString):
    project = partial(
        pyproj.transform,
        pyproj.Proj(init='epsg:4326'),
        pyproj.Proj(projString)
    )
    transformed = mapping(transform(project, shape(geometry)))

    return [transformed]


@girder_job(title='Clip Task')
@app.task(bind=True)
def clip_task(self, girderFile, geometry, name):
    with rasterio.open(girderFile) as src:
        geom = reprojectGeometry(geometry, src.crs.to_string())
        outImage, outTransform = mask(src,
                                      geom,
                                      crop=True)
        outMeta = src.meta.copy()

    outMeta.update({"driver": "GTiff",
                    "height": outImage.shape[1],
                    "width": outImage.shape[2],
                    "transform": outTransform})

    tempName = os.path.join("/tmp", next(tempfile._get_candidate_names()) + "-" + name)
    with rasterio.open(tempName, "w", **outMeta) as dest:
        dest.write(outImage)

    return tempName
