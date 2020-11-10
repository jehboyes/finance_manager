from setuptools import setup

setup(
    name='finance_manager',
    version='0.1',
    py_modules=['finance_manager'],
    use_incremental=True,
    setup_requires=['incremental'],
    install_requires=[
        'incremental',
        'Click',
    ],
    entry_points='''
        [console_scripts]
        fm=finance_manager.cli:fm
    ''',
)
