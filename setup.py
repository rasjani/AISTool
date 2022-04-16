from setuptools import setup, find_packages
from subprocess import check_output
from pathlib import Path
import os
from importlib.util import module_from_spec, spec_from_file_location

NAME="AISTool"
CWD = Path(__file__).parent
requirements_file = CWD / "requirements.txt"
readme_file = CWD / "README.md"
# Get requirements
with requirements_file.open(encoding="utf-8") as f:
    REQUIREMENTS = f.read().splitlines()

# Get the long description from the README file
with readme_file.open(encoding="utf-8") as f:
    long_description = f.read()

CLASSIFIERS = """
Development Status :: 3 - Alpha
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
""".strip().splitlines()

def get_version_and_cmdclass(pkg_path):
    spec = spec_from_file_location("version", os.path.join(pkg_path, "_version.py"))
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__version__, module.get_cmdclass(pkg_path)


version, cmdclass = get_version_and_cmdclass(r".")

setup(
    name=f"{NAME}",
    version=version,
    cmdclass=cmdclass,
    description="Generate ssh config file from Ansible inventory",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Jani Mikkonen",
    author_email="jani.mikkonen@gmail.com",
    url="https://github.com/rasjani/AISTool",
    license="MIT",
    classifiers=CLASSIFIERS,
    packages=[NAME],
    entry_points={
        'console_scripts': [
            f'{NAME}=AISTool.main:main'
        ],
    },
    install_requires=REQUIREMENTS,
    python_requires=">=3.7"
)
