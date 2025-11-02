#!/usr/bin/env python3

from distutils.core import setup
import os

setup(
    name='mate-gpu-applet',
    version='1.0.0',
    description='MATE Panel GPU Monitor Applet',
    author='Your Name',
    author_email='your.email@example.com',
    scripts=['mate_gpu_applet.py'],
    data_files=[
        ('/usr/lib/mate-applets/', ['mate_gpu_applet.py']),
        ('/usr/share/mate-panel/applets/', ['org.mate.panel.GPUApplet.mate-panel-applet']),
        ('/usr/share/applications/', ['mate-gpu-applet.desktop']),
    ],
)
