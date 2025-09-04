#!/usr/bin/env bash
# A small utility bash script to automate the execution of pyfault run on black for various bugs,
# collect the report.json, remove created files and directories and recreate a new shell
# it also runs the setup.sh script
# NOTE: execute the script with source run_test.sh <bug_number> not as ./run_test.sh <bug_number>

conda activate venv
./setup.sh
source black-bugs/bin/activate
cd black
pyfault run
cd ..
mv black/report.json ./
rm -rf black black-bugs bugsinpy-mf
exec bash
