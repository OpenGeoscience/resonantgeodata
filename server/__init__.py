from .rest import RasterTasksEndpoints


def load(info):
    info['apiRoot'].raster = RasterTasksEndpoints()
