from setuptools import setup

with open('./requirements.txt', 'r') as requirements:
    requirements = requirements.read().split('\n')

setup(
    name='autofeepolicy',
    install_requires=requirements
)