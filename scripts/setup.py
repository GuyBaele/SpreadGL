import os
from setuptools import find_packages, setup

with open('requirements.txt') as f:
    requirements = f.readlines()

# Check if conda is installed
conda_env = os.environ.get('CONDA_PREFIX') or os.environ.get('CONDA_DEFAULT_ENV')

if conda_env:
    print(f"Conda environment detected: {conda_env}.\nMake sure dependencies were installed using conda.")
else:
    print("No conda environment detected. Using system Python.\nDependencies will be installed using pip.")

setup(
    name='processing_toolkit',
    version='1.1.0',
    author='Yimin Li',
    author_email='florent.li@kuleuven.be',
    url='https://github.com/GuyBaele/SpreadGL',
    packages=find_packages(),
    entry_points={
            'console_scripts': [
                'spread = spatial_layer_generator.spread:main',
                'rates = bayes_factor_test.rates:main',
                'regions = environmental_layer_generator.regions:main',
                'raster = environmental_layer_generator.raster:main',
                'reprojection = projection_transformation.reprojection:main',
                'trimming = outlier_detection.trimming:main'
            ]},
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements if not conda_env else []
)
