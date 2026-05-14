from setuptools import setup
import os
from glob import glob

package_name = 'marvincar_bringup'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share',package_name,'launch'),glob(os.path.join('launch','*launch.py'))),
        #(os.path.join('share','marvincar_description','urdf'),glob(os.path.join('urdf','*.*'))),
		#(os.path.join('share','marvincar_description','meshes'),glob(os.path.join('meshes','*.*'))),
        (os.path.join('share','marvincar_description','rviz'),glob(os.path.join('rviz','*.rviz*'))),
        (os.path.join('share', package_name, 'param'), glob(os.path.join('param', '*.yaml'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='nx-ros2',
    maintainer_email='nx-ros2@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'Ackman_driver	= marvincar_bringup.Ackman_driver:main',
            'calibrate_linear = marvincar_bringup.calibrate_linear:main',
            'calibrate_angular = marvincar_bringup.calibrate_angular:main',
            'patrol = marvincar_bringup.patrol:main',   
        ],
    },
)
