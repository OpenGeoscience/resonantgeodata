from girder.api import access
from girder.api.describe import autoDescribeRoute, Description
from girder.api.rest import Resource
from girder.constants import AccessType
from girder.models.item import Item
from girder.models.folder import Folder
from girder_worker_utils.transforms.girder_io import GirderFileId
from girder_worker_utils.transforms.girder_io import GirderUploadToItem
from girder_raster_tasks.tasks import clip_task, reproject_task


class RasterTasksEndpoints(Resource):
    def __init__(self):
        super(RasterTasksEndpoints, self).__init__()
        self.route('GET', ('clip', ), self.run_clip_task)
        self.route('GET', ('reproject', ), self.run_reproject_task)

    @access.public
    @autoDescribeRoute(
        Description('Clip a raster with a json geometry')
        .modelParam('itemId', 'The ID of the item that has a raster file',
                    model=Item, level=AccessType.READ, destName='item', paramType='query')
        .jsonParam('geometry', 'Json geometry to clip the raster',
                   requireObject=True)
        .param('name', 'Name of the item', paramType='query')
        .modelParam('folderId', 'Output folder id for the result item',
                    paramType='query', destName='folder', model=Folder, level=AccessType.READ)
    )
    def run_clip_task(self, item, geometry, name, folder):
        girderFile = [i for i in Item().childFiles(item, limit=1)][0]
        output = Item().createItem(name,
                                   creator=self.getCurrentUser(),
                                   folder=folder)
        result = clip_task.delay(GirderFileId(str(girderFile['_id'])),
                                 geometry,
                                 name,
                                 girder_result_hooks=[
                                     GirderUploadToItem(str(output['_id']))
                                 ])
        return result.job

    @access.public
    @autoDescribeRoute(
        Description('Reproject a raster with a given crs and resampling method')
        .modelParam('itemId', 'The ID of the item that has a raster file',
                    model=Item, level=AccessType.READ, destName='item', paramType='query')
        .param('crs', 'Proj4 string to reproject')
        .param('resampling', 'Resampling method', default='nearest')
        .param('name', 'Name of the item', paramType='query')
        .modelParam('folderId', 'Output folder id for the result item',
                    paramType='query', destName='folder', model=Folder, level=AccessType.READ)
    )
    def run_reproject_task(self, item, crs, resampling, name, folder):
        girderFile = [i for i in Item().childFiles(item, limit=1)][0]
        output = Item().createItem(name,
                                   creator=self.getCurrentUser(),
                                   folder=folder)
        result = reproject_task.delay(
            GirderFileId(str(girderFile['_id'])),
            name,
            crs,
            resampling,
            girder_result_hooks=[
                GirderUploadToItem(str(output['_id']))
            ])
        return result.job
