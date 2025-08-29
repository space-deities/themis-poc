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

- **FOPs core** (tracing / retry / sinks) + **domain specific directives**
- A **VS Code extension** that raises prompts and returns operator responses to Python over HTTP
- A **Python integration** that asks the VS Code extension for input (retry decorator with console fallback)

---

## Quickstart

1. Setup the build environment:  
```bash
python3 -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install hatch
```
2. Build the lib:
```bash
hatch build
```

3. The library is generated in ./dist. E.g.:
```bash
ls -l dist
-rw-r--r--@ 1 cestevez  staff  30640 Aug 23 23:14 themis_fop_core-0.1.0-py3-none-any.whl
-rw-r--r--@ 1 cestevez  staff  30172 Aug 23 23:14 themis_fop_core-0.1.0.tar.gz
```


> Tip: TBD.

---

## Configuration

### Supported envs

---
