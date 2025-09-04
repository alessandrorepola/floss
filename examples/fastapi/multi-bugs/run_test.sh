#!/usr/bin/env bash
# A small utility bash script to automate the execution of floss run on fastapi for various bugs,
# collect the report.json, remove created files and directories and recreate a new shell
# it also runs the setup.sh script
# NOTE: execute the script with source run_test.sh <bug_number> not as ./run_test.sh <bug_number>

conda activate venv
./setup.sh
source fastapi-bugs/bin/activate
cd fastapi
floss run
cd ..
mv fastapi/report.json ./
rm -rf fastapi fastapi-bugs bugsinpy-mf
exec bash
