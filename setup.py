import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open(os.path.join("peakrdl", "python", "__about__.py")) as f:
    v_dict = {}
    exec(f.read(), v_dict)
    version = v_dict['__version__']

setuptools.setup(
    name="peakrdl-python",
    version=version,
    author="Keith Brady",
    description="Generate python wrapper for a register model compiled SystemRDL input",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/krcb197/PeakRDL-python",
    packages=['peakrdl.python'],
    include_package_data=True,
    entry_points= { 'console_scripts' : ['peakpython=peakrdl.python.peakpython:main_function'] },
    install_requires=[
        "systemrdl-compiler>=1.12.0",
        "autopep8",
        "pylint",
        "coverage",
        "jinja2",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
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
