from setuptools import setup
import os
from glob import glob

package_name = 'marvincar_camera'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob(os.path.join('launch', '*launch.py'))),
        (os.path.join('share', package_name, 'param'),
            glob(os.path.join('param', '*.yaml'))),
    ],
    install_requires=['setuptools', 'opencv-python'],
    zip_safe=True,
    maintainer='carlosalegrias',
    maintainer_email='example@todo.todo',
    description='Camera driver node for MARVIN robot - publishes USB camera streams',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'camera_node = marvincar_camera.camera_node:main',
        ],
    },
)
