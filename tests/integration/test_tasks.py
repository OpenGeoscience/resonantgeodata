import json
import os
import time
import pytest


def _waitForJob(gc, jobId):
    # Wait for the clip job to be completed
    timeout = 10
    while timeout > 0:
        time.sleep(1)
        job = gc.get('job/{}'.format(jobId))
        if job['status'] == 3:
            timeout = 0
        else:
            timeout -= 1


def _uploadFile(gc, admin, tiff):
    public = gc.resourceLookup('/user/{}/Public'.format(admin['login']))
    size = os.stat(tiff).st_size
    with open(tiff, 'rb') as f:
        uploaded = gc.uploadFile(public['_id'],
                                 f,
                                 name=os.path.basename(tiff),
                                 size=size,
                                 parentType='folder')

    return uploaded


@pytest.mark.plugin('resonantgeodata')
@pytest.mark.plugin('worker')
def test_clip_task(admin, db, liveServer, fsAssetstore):
    liveServer.authenticate(admin['login'], 'password')
    # Set worker url
    liveServer.put('system/setting', parameters={'key': 'worker.api_url',
                                                 'value': liveServer.urlBase[:-1]})

    public = liveServer.resourceLookup('/user/{}/Public'.format(admin['login']))
    sampleTiff = 'tests/data/chicago.tif'
    output = 'clipped.tif'
    uploaded = _uploadFile(liveServer, admin, sampleTiff)
    geometry = 'tests/data/geometry.json'

    with open(geometry) as f:
        data = json.load(f)

    job = liveServer.get('raster/clip', parameters={
        'itemId': uploaded['itemId'],
        'geometry': json.dumps(data),
        'name': output,
        'folderId': public['_id']
    })

    _waitForJob(liveServer, job['_id'])
    resultFile = liveServer.get('resource/search', parameters={
        'q': output,
        'types': '["file"]'
    })

    assert resultFile['file'][0]['size'] > 0


@pytest.mark.plugin('resonantgeodata')
@pytest.mark.plugin('worker')
def test_reproject_task(admin, db, liveServer, fsAssetstore):
    liveServer.authenticate(admin['login'], 'password')
    # Set worker url
    liveServer.put('system/setting', parameters={'key': 'worker.api_url',
                                                 'value': liveServer.urlBase[:-1]})

    public = liveServer.resourceLookup('/user/{}/Public'.format(admin['login']))
    sampleTiff = 'tests/data/chicago.tif'
    output = 'reprojected.tif'
    uploaded = _uploadFile(liveServer, admin, sampleTiff)

    job = liveServer.get('raster/reproject', parameters={
        'itemId': uploaded['itemId'],
        'crs': '+proj=merc +lon_0=0 +k=1 +x_0=0 +y_0=0 +a=6378137 +b=6378137 +units=m +no_defs ',
        'name': output,
        'folderId': public['_id']
    })

    _waitForJob(liveServer, job['_id'])
    resultFile = liveServer.get('resource/search', parameters={
        'q': output,
        'types': '["file"]'
    })

    assert resultFile['file'][0]['size'] > 0
