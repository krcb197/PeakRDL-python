import os
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open(os.path.join("src", "peakrdl_python", "__about__.py")) as f:
    v_dict = {}
    exec(f.read(), v_dict)
    version = v_dict['__version__']

setup(
    name="peakrdl-python",
    version=version,
    author="Keith Brady",
    description="Generate python wrapper for a register model compiled SystemRDL input",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/krcb197/PeakRDL-python",
    package_dir={'': 'src'},
    packages=[ 'peakrdl_python',
               'peakrdl.python'],   # backwards compatibility shim
    package_data={"peakrdl_python.templates": ["*.py.jinga"]},
    include_package_data = True,
    entry_points= { 'console_scripts' : ['peakrdl_python=peakrdl_python.peakpython:main_function'],
                    "peakrdl.exporters": [
                        'python = peakrdl_python.__peakrdl__:Exporter'
                    ]
                    },
    install_requires=[
        "systemrdl-compiler>=1.21.0",
        "autopep8",
        "pylint",
        "coverage",
        "jinja2",
        "peakrdl-ipxact"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
    ],
    project_urls={
        "Source": "https://github.com/krcb197/PeakRDL-python",
        "Tracker": "https://github.com/krcb197/PeakRDL-python/issues",
        "Documentation": "https://peakrdl-python.readthedocs.io/"
    },
)
