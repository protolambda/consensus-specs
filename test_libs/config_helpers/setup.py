from distutils.core import setup

setup(
    name='config_helpers',
    version='1.0',
    packages=['preset_loader'],
    install_requires=[
        "ruamel.yaml==0.15.87"
    ]
)
