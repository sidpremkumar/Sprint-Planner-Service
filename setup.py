# Local Modules
from setuptools import setup

with open('requirements.txt', 'rb') as f:
    install_requires = f.read().decode('utf-8').split('\n')

setup(
    name='Sprint Planning Utility',
    version=1.0,
    description="Plans sprint information for JIRA projects",
    author='Sid Premkumar',
    author_email='sid.premkumar@gmail.com',
    url='https://github.com/sidpremkumar/Sprint-Planning-Utility',
    license='',
    install_requires=install_requires,
    packages=[
        'SPU'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            "spu=SPU.main:main",
        ],
    },
)