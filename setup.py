from setuptools import setup

setup(
    name='pom-helper',
    author='applerodite',
    version='0.1',
    packages=['pom_helper'],
    description='A helper for parsing `.pom`',
    include_package_data=True,
    exclude_package_data={'docs': ['README.md']},
    install_requires=[
        'lxml', 'requests', 'attrs'
    ],
    extras_require={'test': ['pytest']}
)
