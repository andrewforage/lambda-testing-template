"""
Copy a file as /tmp/test_file.patch

Example:
python utils/cp_patch.py sample_patches/task1/py3/mod1_calvin.patch

"""

import os
import sys
from shutil import copyfile

if __name__ == '__main__':
    TEST_FILE_FOLDER = "/tmp/"
    TEST_FILE_PATH = TEST_FILE_FOLDER + "test_file.patch"
    new_file = sys.argv[1]
    if os.path.exists(TEST_FILE_PATH):
        os.remove(TEST_FILE_PATH)
    try:
        new_file = sys.argv[1]
        # if new_file.endswith(".patch"):
        fn = new_file.split("/")[-1]
        copyfile(new_file, TEST_FILE_PATH)
        print("Copied " + new_file + "to " + TEST_FILE_PATH)
        # else:
        #     print("Invalid patch path")
    except:
        print("Make sure patch path is valid")
