import setuptools
version = {}
with open("finance_manager/_version.py") as fp:
    exec(fp.read(), version)


# later on we use: version['__version__']
setuptools.setup(
    name='finance_manager',
    version=version['__version__'],
    py_modules=['finance_manager'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        fm=finance_manager.cli:fm
    ''',
    packages=setuptools.find_packages()
)
