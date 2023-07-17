from setuptools import setup

setup(
    name="SPC",
    version="0.1.0",
    description='Quick SPC-style plotting using the Plotly framework.',
    author="Tarik Basic",
    author_email="tbasic@ucsd.edu",
    url="https://github.com/DryBasic/SPC-Plot",
    packages=['SPC'],
    install_requires=['pandas', 'plotly'],
)
