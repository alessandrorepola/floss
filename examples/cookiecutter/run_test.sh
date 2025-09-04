#!/usr/bin/env bash
# A small utility bash script to automate the execution of floss run on cookiecutter for various bugs,
# collect the report.json, remove created files and directories and recreate a new shell
# it also runs the setup.sh script
# NOTE: execute the script with source run_test.sh <bug_number> not as ./run_test.sh <bug_number>

BUG_NUMBER="$1"
conda activate venv
./setup.sh "$BUG_NUMBER"
source cc-bug"$BUG_NUMBER"/bin/activate
cd cookiecutter
floss run
cd ..
mkdir bug"$BUG_NUMBER"
mv cookiecutter/report.json ./bug"$BUG_NUMBER"
mv BugsInPy/projects/cookiecutter/bugs/"$BUG_NUMBER"/bug_patch.txt ./bug"$BUG_NUMBER"
rm -rf cookiecutter cc-bug"$BUG_NUMBER" BugsInPy
exec bash
