import sys
import os

from ez_setup import use_setuptools
use_setuptools('0.6c3')

from setuptools import setup, find_packages, Extension
from distutils.sysconfig import get_python_inc
from glob import glob
import commands


dist = setup( name='shr-settings',
    version='0.1.1',
    author='dos',
    author_email='seba.dos1@gmail.com',
    description='Modular settings application for SHR based on python-elementary',
    url='http://shr-project.org/',
    download_url='git://git.shr-project.org/repo/shr-settings.git',
    license='GNU GPL',
    packages=['shr_settings_modules'],
    scripts=['shr-settings'],
    data_files=[('pixmaps', ['data/shr_settings.png']),
		('pixmaps/shr-settings' , glob("data/icons/*.png")),
		('applications/shr-settings-addons-illume', glob("data/shr-settings-addons-illume/*.desktop")),
		('applications', ['data/shr-settings.desktop']),
		('locale/ar/LC_MESSAGES', ['data/po/ar/shr-settings.mo']),
		('locale/ca/LC_MESSAGES', ['data/po/ca/shr-settings.mo']),
		('locale/cs/LC_MESSAGES', ['data/po/cs/shr-settings.mo']),
		('locale/da/LC_MESSAGES', ['data/po/da/shr-settings.mo']),
		('locale/de/LC_MESSAGES', ['data/po/de/shr-settings.mo']),
		('locale/es/LC_MESSAGES', ['data/po/es/shr-settings.mo']),
		('locale/it/LC_MESSAGES', ['data/po/it/shr-settings.mo']),
		('locale/nb/LC_MESSAGES', ['data/po/nb/shr-settings.mo']),
		('locale/pl/LC_MESSAGES', ['data/po/pl/shr-settings.mo']),
		('locale/ru/LC_MESSAGES', ['data/po/ru/shr-settings.mo']),
		('../../etc/shr-settings', ['config/backup.conf', 'config/backup.whitelist', 'config/backup.blacklist'])
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

