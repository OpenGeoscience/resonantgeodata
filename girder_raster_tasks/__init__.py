# -*- coding: utf-8 -*-

"""Top-level package for Girder Raster Tasks."""

__author__ = """Kitware Inc"""
__email__ = 'kitware@kitware.com'
__version__ = '0.0.0'


from girder_worker import GirderWorkerPluginABC


class GirderRasterTasks(GirderWorkerPluginABC):
    def __init__(self, app, *args, **kwargs):
        self.app = app

    def task_imports(self):
        return ['girder_raster_tasks.tasks']
