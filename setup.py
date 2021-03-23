import setuptools
version = {}
with open("finance_manager/_version.py") as fp:
    exec(fp.read(), version)

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name='finance_manager',
    version=version['__version__'],
    py_modules=['finance_manager'],
    install_requires=[
        'Click',
    ],
    author="James Boyes",
    author_email="James.Boyes@lcm.ac.uk",
    description="Managing HE Financial Forecasting and Planning",
    entry_points='''
        [console_scripts]
        fm=finance_manager.cli:fm
    ''',
    long_description=long_description,
    url="https://github.com/jehboyes/finance_manager",
    packages=setuptools.find_packages()
)
