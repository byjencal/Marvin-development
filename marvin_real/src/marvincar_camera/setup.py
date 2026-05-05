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
            glob(os.path.join('launch', '*launch.py')))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='carlos',
    maintainer_email='carlos@todo.todo',
    description='CSI camera nodes for IMX219 cameras',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'camera_csi0 = marvincar_camera.camera_csi0_node:main',
            'camera_csi1 = marvincar_camera.camera_csi1_node:main',
        ],
    },
)
