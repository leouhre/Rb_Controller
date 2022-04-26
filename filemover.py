import shutil, os
from pathlib import Path

p = Path.cwd()

if not p.exists:
    os.makedirs(p / "quiz_program")

for i in range(35):
    
    shutil.move(p / f"capitalsquiz_answers{i + 1}.txt", p / "quiz_program")
    shutil.move(p / f"capitalsquiz{i + 1}.txt", p / "quiz_program")
