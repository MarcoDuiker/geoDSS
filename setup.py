from setuptools import setup, find_packages

long_description = """
geoDss is a library to quickly evaluate a subject against rules.
"""

setup(
    name='geoDSS',
    version='0.5',
    description='geoDSS',
    long_description=long_description,
    url='',
    author='Marco Duiker',
    author_email='md@md-kwadraat.nl',
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='',
    packages=find_packages(exclude=[])
)
