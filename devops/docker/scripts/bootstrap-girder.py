import os
import time
import girder_client
import ConfigParser

try:
    from urllib2 import urlopen, URLError
except ImportError:
    from urllib.request import urlopen, URLError


def waitForIt(url, timeout=5):
    # Wait for girder to be up and running
    while timeout > 0:
        time.sleep(1)
        try:
            urlopen(url)
            timeout = 0
        except URLError:
            timeout -= 1

def getGirderUrlFromConfig():
    config = ConfigParser.ConfigParser()
    config.read('/root/.girder/girder.cfg')
    host = config.get('global', 'server.socket_host').strip("'\"")
    port = config.get('global', 'server.socket_port').strip("'\"")
    apiRoot = config.get('server', 'api_root').strip("'\"")
    return 'http://{}:{}/{}'.format(host, port, apiRoot)


gc = girder_client.GirderClient(apiUrl='http://girder:8989/api/v1')

# Create admin user
admin = gc.createUser('admin', 'admin@admin.com', 'Admin',
                      'Admin', 'letmein', admin=True)

# Restart girder and wait for it to be up
gc.authenticate('admin', 'letmein')

# Create filesystem assetstore
assetstore = gc.post('/assetstore', parameters={'name': 'assetstore',
                                                'type': 0,
                                                'root': '/tmp/assetstore'})

# Enable necessary plugins
gc.put('/system/plugins', parameters={
    'plugins': '["geometa", "resonantgeodata", "large_image", "ess_dive"]'
})

gc.post('/system/web_build')

# Upload directory to girder
public = gc.get('/resource/search', parameters={
    'q': 'Public',
    'types': '["folder"]'
})

data_path = '/resonantgeodata/devops/docker/data'
if os.path.exists(data_path):
    gc.upload('{}/*'.format(data_path), public['folder'][0]['_id'])

gc.put('/system/restart')

waitForIt(getGirderUrlFromConfig(), timeout=30)

# Set girder worker related settings
gc.put('/system/setting', parameters={
    'key': 'worker.broker',
    'value': 'amqp://guest:guest@rabbitmq/',
})

gc.put('/system/setting', parameters={
    'key': 'worker.backend',
    'value': 'amqp://guest:guest@rabbitmq/'
})

gc.put('/system/setting', parameters={
    'key': 'worker.api_url',
    'value': 'http://girder:8989/api/v1'
})

gc.put('/system/setting', parameters={
    'key': 'core.server_root',
    'value': 'http://girder:8989'
})
