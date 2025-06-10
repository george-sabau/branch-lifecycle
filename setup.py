from setuptools import setup, find_packages

setup(
    name='branch-lifecycle',
    version='0.1.0',
    author='George Sabau',
    author_email='ges@foryouandyourcustomers.com',
    description='Git Branch Lifecycle Analysis Tool',
    packages=find_packages(),
    install_requires=[
        'PyYAML',
        'GitPython',
        'numpy',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)