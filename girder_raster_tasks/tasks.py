from functools import partial
import os
import tempfile
import pyproj

import rasterio
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject
from rasterio.mask import mask
from shapely.ops import transform
from girder_worker.app import app
from girder_worker.utils import girder_job
from shapely.geometry import shape, mapping


def reprojectGeometry(geometry, projString):
    inProj = pyproj.Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs ')
    outProj = pyproj.Proj(projString)
    project = partial(
        pyproj.transform,
        inProj,
        outProj
    )
    transformed = mapping(transform(project, shape(geometry)))

    return [transformed]


def getTempFileName(name):
    tempName = next(tempfile._get_candidate_names()) + "-" + name
    return os.path.join("/tmp", tempName)


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

    tempName = getTempFileName(name)

    with rasterio.open(tempName, "w", **outMeta) as dest:
        dest.write(outImage)

    return tempName


@girder_job(title='Reproject Task')
@app.task(bind=True)
def reproject_task(self, girderFile, name, dstCrs, resampleMethod):
    tempName = getTempFileName(name)
    dstCrs = str(dstCrs)
    with rasterio.open(girderFile) as src:
        affine, width, height = calculate_default_transform(
            src.crs, dstCrs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dstCrs,
            'transform': affine,
            'affine': affine,
            'width': width,
            'height': height
        })

        with rasterio.open(tempName, 'w', **kwargs) as dest:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dest, i),
                    src_transform=affine,
                    src_crs=src.crs,
                    dst_transform=affine,
                    dst_crs=dstCrs,
                    resampling=getattr(Resampling, resampleMethod))

    return tempName
