from setuptools import find_packages, setup

with open('requirements.txt') as f:
    requirements = f.readlines()

setup(
    name='processing_toolkit',
    version='1.0.0',
    author='Yimin Li',
    author_email='florent.li@kuleuven.be',
    url='https://github.com/GuyBaele/SpreadGL',
    packages=find_packages(),
    entry_points={
            'console_scripts': [
                'spatial = spatial_layer_generator.spatial:main',
                'environmental = environmental_layer_generator.environmental:main',
                'reprojection = projection_transformation.reprojection:main',
                'trimming = outlier_detection.trimming:main'
            ]},
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements
)