from setuptools import setup, find_packages
import depends


classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities'
]

setup(
    name='Depends',
    version=depends.version,
    description='quality assurance for content',
    long_description=open('README.txt').read(),
    author='Andrew Gardner',
    author_email='andrew.gardner@liu.se',
    url='https://github.com/mottosso/dependsworkflow',
    license="LICENSE.txt",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=classifiers,
    package_data={
        'depends': [
            'depends',
            '*.stylesheet',
            'data_packets/*.py',
            'doc/*.txt',
            'file_dialogs/*.py',
            'nodes/*.py',
            'output_recipes/*.py',
        ]
    },
)
