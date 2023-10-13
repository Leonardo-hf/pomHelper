from setuptools import setup, find_packages

setup(
    name='pom-helper',
    author='applerodite',
    version='0.1',
    packages=find_packages(),
    description='',
    py_modules=['pom_helper'],
    include_package_data=True,
    exclude_package_data={'docs': ['README.md']},
    install_requires=[
        'lxml', 'requests',
    ],
)
