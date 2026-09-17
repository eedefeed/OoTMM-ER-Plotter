# Notes 

This guide is not for regular users of OoTMM ER Plotter.

The two ways of using OoTMM ER Plotter are as follows:
1. Using the executables
2. Executing main.py with python

For instructions on those methods, please see (README.md)[README.md]

# Building executable files

You may have already performed some of these steps as a user of OoTMM ER Plotter. There should be no need to repeat them.

1. Create virtual environment
```python -m venv venv```

2. Activate virtual environment
Linux: `source venv/bin/activate`
Windows: `.\venv\Scripts\activate`

3. Install requirements
`pip install -r requirements.txt`

4. Install pyinstaller:
```pip install pyinstaller```

5. Build:
```py -m PyInstaller .\main.spec```

Warning: some PyInstaller commands will overwrite `.\main.spec` with a default script. If things aren't working, try checking the contents of the file have not been editted. 

This final command builds an executable and creates a few folders and files. 

Your executable will be found in `./dist/`. If you're on windows, it'll be a windows executable. If you're on linux, it'll be some sort of linux executable.

# Troubleshooting

## Module Not Found: pkg_resources

If you get a stack traces which ends with: `ModuleNotFoundError: No module named 'pkg_resources'` then you may have somehow ended up with the wrong version of setuptools. 

Verify this **in your venv** by executing `pip list`. setuptools should be version 81.0.0. Previous versions should work fine. Later versions will not work.

The solution is to install the correct version of setuptools.

(This is a problem with gravis module)

## pyinstaller command not found

See: https://pyinstaller.org/en/v6.22.3/installation.html#troubleshooting-missing-pyinstaller-command