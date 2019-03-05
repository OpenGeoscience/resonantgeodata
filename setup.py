from setuptools import setup, find_packages

with open('README.rst', 'r') as fh:
    long_desc = fh.read()

setup(name='girder_raster_tasks',
      version='0.0.0',
      description='Raster tasks for Girder with rasterio',
      long_description=long_desc,
      author='Kitware Inc',
      author_email='kitware@kitware.com',
      license='Apache Software License 2.0',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'License :: OSI Approved :: Apache Software License',
          'Topic :: Scientific/Engineering',
          'Intended Audience :: Science/Research',
          'Natural Language :: English',
          'Programming Language :: Python'
      ],
      install_requires=[
          'mock',
          'girder_worker',
          'girder_worker_utils',
          'rasterio',
          'shapely',
          'pyproj'
      ],
      include_package_data=True,
      entry_points={
          'girder_worker_plugins': [
              'girder_raster_tasks = girder_raster_tasks:GirderRasterTasks',
          ]
      },
      packages=find_packages(),
      zip_safe=False)
