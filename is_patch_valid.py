"""
InsideSherpa.com - Flask Testing Template

Description:
- This template creates a Flask app to perform a basic test and return results in a Python dictionary in console
"""

from flask import Flask, request, jsonify
from io import StringIO
import json
import sys
import re
import unittest
import subprocess
import os
import contextlib
import requests
import random
import shutil
import git

app = Flask(__name__)
lambda_api_key = 'testing'
###################################################
# You should not need to edit any of the code above

# Write your Python unit test here
class TestPatchFile(unittest.TestCase):
    def test_general(self):
        print("Running is_patch_valid")

        ## Replace later to make it general
        PATCH_PATH = "/tmp/test_file.patch"

        try:
            if PATCH_PATH.endswith(".patch"):

                ## Load patch
                output = subprocess.Popen(['cat', PATCH_PATH], cwd=os.getcwd(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                output.wait()
                buffer = output.stdout
                lines = buffer.readlines()


                ## Clean text
                ### Convert to clean strings
                lines = [x.decode("utf-8").strip() for x in lines]


                ### Remove empty lines
                lines = [x for x in lines if x!=""]


                ## Example: Valid header
                """
                From 92338535dbd92626397ad8a27c24a4b1ebf4ca94 Mon Sep 17 00:00:00 2001
                From: Calvin Pang <calvinpang195@gmail.com>
                Date: Thu, 31 Oct 2019 17:22:19 +0000
                Subject: [PATCH] INIT

                ---
                 client3.py | 31 +++++++++++++++----------------
                 1 file changed, 15 insertions(+), 16 deletions(-)
                """


                ## Check if the patch follows the same format
                valid = lines[0].startswith("From ")
                valid = valid & lines[1].startswith("From: ")
                valid = valid & lines[2].startswith("Date: ")
                valid = valid & lines[3].startswith("Subject: ")


                ### Check whether diff exists and if its location is valid
                start_of_diff = -1
                for i in range(len(lines)):
                    if lines[i].startswith("diff "):
                        start_of_diff = i
                valid = valid & (start_of_diff > 4)


                ### Check if the line containing "x file/s changed,..." exists
                ln_num__num_files_changed = -1
                for i in range(len(lines)):
                    if "files changed" in lines[i] or "file changed" in lines[i]:
                        ln_num__num_files_changed = i
                valid = valid & (ln_num__num_files_changed < start_of_diff)


                ## Example: Valid footers
                """
                --
                2.11.0
                """
                """
                --
                2.20.1 (Apple Git-117)
                """
                """
                --
                2.24.0.windows.1
                """

                ## Check if the git version of the patch is valid
                valid = valid & (lines[-1].count(".") >= 2)

                ## Return result
                print("is_patch_valid: Passed")
                self.assertTrue(valid)
            else:
                print("is_patch_valid: Failed")
                self.assertTrue(False)
        except:
            print("is_patch_valid: Failed")
            self.assertTrue(False)



"""
This will clone the repository: https://github.com/insidesherpa/JPMC-tech-task-1.git
into /tmp/<randomNumber>/taskDir and then apply the git patch file located at /tmp/test_file.patch to the git repo.
"""
def run_tests(fileLocation):
    tests_failed = []
    import __main__
    failed_patch = False
    os.chdir('/tmp')
    git_dir = 'JPMC-tech-task-1-PY3'
    random_num = random.randint(100000, 1000000)
    git_url = 'https://github.com/insidesherpa/JPMC-tech-task-1-PY3.git'
    # Git clone into custom directory and apply patch file
    new_repo_path = "%s/%s/taskDir" % (os.getcwd(), random_num)
    if not os.path.exists(new_repo_path):
        os.makedirs(new_repo_path)
        git_output = git.exec_command('clone', git_url, cwd=new_repo_path)
        print ("successfully created clone of repo")
        print (git_output)
        repo_path = '%s/%s/taskDir/%s' % (os.getcwd(), random_num, git_dir)
        os.chdir(repo_path)
        try:
            output = git.exec_command('apply', '/tmp/test_file.patch', cwd=os.getcwd())
        except Exception as error:
            failed_patch = True
    else:
        repo_path = '%s/%s/taskDir/%s' % (os.getcwd(), random_num, git_dir)
        os.chdir(repo_path)


    # Runs unittest and outputs into buf
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    with StringIO() as buf:
        if (not failed_patch):
            with redirect_stdout(buf):
                unittest.TextTestRunner(stream=buf).run(suite)
            test_output = buf.getvalue()
            print (test_output)
            didnt_run = re.compile("Ran 0 test.*")
            all_tests = didnt_run.findall(test_output)
        if (failed_patch):
            tests_failed = ['FAIL. Failed to apply patch']
        elif (len(all_tests) > 0):
            tests_failed = all_tests
        else:
            # Find all fail tests using Regex and return as an array
            find_fails = re.compile('FAIL.*')
            all_fails = find_fails.findall(test_output)
            tests_failed = all_fails

    # Clean git clone directory
    os.chdir('/tmp')
    pathToDelete = "%s/%s" % (os.getcwd(), random_num)
    if (os.path.exists(pathToDelete)):
        shutil.rmtree(pathToDelete)
    return tests_failed

# You should not need to edit any code below
############################################
# Parse content from stdout for reading tests output
@contextlib.contextmanager
def redirect_stdout(target):
    original = sys.stdout
    sys.stdout = target
    yield
    sys.stdout = original

def handle_async_marking(deliverable):
    # Place your patch file to test in the downloadLoc path
    # Assumes / simulates we've already downloaded the file from S3
    downloadLoc = '/tmp/test_file.patch'

    # Run tests and store failed results as array
    failed_tests = run_tests(downloadLoc)

    # Fire callback to callback URL
    callback = {
        'marked': True,
        'testsFailed': len(failed_tests),
        'testResults': failed_tests,
    }
    print('Printing callback')
    print(callback)

@app.route('/test', methods=['GET', 'POST'])
def begin_patch_test():
    """
    LOGIC:
    1. Receives JSON Post request
    2. Downloads response from S3 (for testing we use file from local machine)
    3. Runs tests below
    4. Returns JSON response of successful tests
    """
    if request.method == 'POST':
        deliverable = request.json
        handle_async_marking(deliverable)
        return jsonify({
            'success': True,
            'message': ('[status] testing request received')
        })
    return jsonify({'error': 'invalid request'})

if __name__ == '__main__':
    app.run(debug=True)
