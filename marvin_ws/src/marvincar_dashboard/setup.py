from setuptools import find_packages, setup

package_name = 'marvincar_dashboard'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='carlos',
    maintainer_email='carlos@example.com',
    description='PyQt5 cockpit dashboard for M.A.R.V.I.N. compressed camera streams.',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'cockpit_node = marvincar_dashboard.cockpit_node:main',
        ],
    },
)
