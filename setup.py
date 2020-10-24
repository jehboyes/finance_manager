from setuptools import setup

setup(
    name='finance_manager',
    version='0.1',
    py_modules=['finance_manager'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        fm=finance_manager.cli:fm
    ''',
)
