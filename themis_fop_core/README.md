# Themis FOP Core

**Status:** Experimental  
This experiment puts in practice the viability of wrapping in a lib the FOP framework.
This lib should include support elements required for implementing any directive, driver or external integration.

At this point, monolitically contains everything (should delegate some features in the future on themis_fop_lang and themis_fop_driver).

---

## Objectives

The aim is to validate that we can wrap in a single python lib the required "run time" for supporting a full FOP lang in top of a python interpreter. This lib will be a key dependency when setting up the fop_runner

---

## What’s Included

- **Themis Core**: A python library implementing themis domain specific directives (Themis Lang), plus helpers for parsing arguments, track the execution of a directive and automatic catch/retry on exceptions (actual Themis Core). These two should be split in the future.
- **Themis Runner**: A container-based solution for running  python scripts. The python is pre-configured with Themis Core, so Themis Lang is enabled for implementing FOPs in python.
- **VS Code extension for Themis** A VS Code extension that creates a panel raising prompts and returning operator responses to the themis script over HTTP.
- **VS Code python integration for Themis** A python extension to Themis Lang that asks the VS Code extension for input (retry decorator with console fallback)

---

## Quickstart

### Themis Core
1. Setup the build environment:  
```bash
cd themis_fop_core
python3 -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install hatch
```
2. Build the lib:
```bash
hatch build
```

> Note: The library is generated in ./dist. E.g.:
> ```bash
> ls -l dist
> -rw-r--r--@ 1 cestevez  staff  30640 Aug 23 23:14 themis_fop_core-0.1.0-py3-none-any.whl
> -rw-r--r--@ 1 cestevez  staff  30172 Aug 23 23:14 themis_fop_core-0.1.0.tar.gz
>>```


3. Test the library via command line, running a python script using Themis Lang for simulating a FOP: 
```bash
cd test
./setup.sh
python fop2.py
```

4. Test the step-by-step execution using VSCode: 
```bash
cd test
./setup.sh
code .
```
* Select fop2.py
* Set a breakpoint (e.g. line 15 - Send COMMAND_B)
* Click on Run&Debug -> 'Python File Debug the current file'
* The debugger should stop on the break point
* Run step by step to the end of the procedure

> Note: In the previous examples, the exceptions are captured and prompt for options are presented in the console. In the next examples, this "prompt on failure" will be redirected to the VSCode extension, so the prompt could be responded via integrated VSCode panel.

---

## Configuration

### Supported envs

---
