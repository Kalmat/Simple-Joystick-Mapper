import io
import os
import re
from setuptools import setup, find_packages

scriptFolder = os.path.dirname(os.path.realpath(__file__))
os.chdir(scriptFolder)

# Find version info from module (without importing the module):
with open("joystickmapper/__init__.py", "r") as fileObj:
    match = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fileObj.read(), re.MULTILINE
    )
    if not match:
        raise TypeError("'__version__' not found in 'joystickmapper/__init__.py'")
    version = match.group(1)

# Use the README.md content for the long description:
with io.open("README.md", encoding="utf-8") as fileObj:
    long_description = fileObj.read()


setup(
    name='joystickmapper',
    version=version,
    url='https://github.com/Kalmat/simple-joystick-mapper',
    # download_url='https://github.com/Kalmat/PyWinCtl/archive/refs/tags/%s.tar.gz' % version,
    author='Kalmat',
    author_email='palookjones@gmail.com',
    description='Controller mapper tool',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    packages=find_packages(),
    package_data={"joystickmapper": ["qss/*.qss"]},
    install_requires=[
        "PyQt5~=5.15.11",
        "pygame~=2.6.1"
    ],
    keywords="controller joystick mapper arcade retro gamepad buttons",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Environment :: MacOS X',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11'
    ],
)
