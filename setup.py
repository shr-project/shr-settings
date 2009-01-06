import sys
import os

from ez_setup import use_setuptools
use_setuptools('0.6c3')

from setuptools import setup, find_packages, Extension
from distutils.sysconfig import get_python_inc
from glob import glob
import commands


dist = setup( name='shr-settings',
    version='0.0.1',
    author='dos',
    author_email='seba.dos1@gmail.com',
    description='Modular settings application for SHR based on python-elementary',
    url='http://shr-project.org/',
    download_url='svn://openmoko.opendevice.org/trunk/shr-settings',
    license='GNU GPL',
    packages=['shr_settings_modules'],
    scripts=['shr-settings'],
    data_files=[('applications', ['data/shr-settings.desktop']),
	('pixmaps', ['data/shr_settings.png'])
        ]
)

installCmd = dist.get_command_obj(command="install_data")
installdir = installCmd.install_dir
installroot = installCmd.root

if not installroot:
    installroot = ""

if installdir:
    installdir = os.path.join(os.path.sep,
        installdir.replace(installroot, ""))

