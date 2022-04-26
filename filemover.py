#Copies test data to a user named directory in "tests"

import shutil, os
from pathlib import Path
import pyinputplus

data_path = Path.cwd() / "data"
test_path = Path.cwd() / "tests" / pyinputplus.inputFilename("Enter name of folder for tests: ")

os.makedirs(test_path)

for i in range(pyinputplus.inputInt("enter number of sensors: ")):
    shutil.copy(data_path / f"sensor{i}.txt", test_path)
shutil.copy(data_path / "time.txt", test_path)

if pyinputplus.inputYesNo("copy voltage?(yes/no): ") == "yes":
    shutil.copy(data_path / "voltage.txt", test_path)
