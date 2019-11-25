"""
InsideSherpa.com - Flask Testing Template

Description:
- This template creates a Flask app to perform a basic test

Task:
- Implement a test that downloads the provided git patch file
"""

from flask import Flask, request, jsonify
from io import BytesIO as StringIO
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

# DEVELOPER TO-DO: Write your Python unit test here
class TestPatchFile(unittest.TestCase):
    def test_general(self):
        print("Running test_general")
        # To indicate the test has passed, assert true
        self.assertTrue(True)

"""
run_tests method will clone the repository e.g. https://github.com/insidesherpa/JPMC-tech-task-1.git
into /tmp/<randomNumber>/taskDir and then apply the git patch file located at /tmp/test_file.patch to the git repo.
if patch is successful, then the unit test(s) in the Test class above will be executed
"""
def run_tests(fileLocation):
    tests_failed = []
    import __main__
    failed_patch = False
    os.chdir('/tmp')
    # DEVELOPER TO-DO: Change the git_dir to the appropriate git directory of the task
    # you're creating test(s) for
    git_dir = 'JPMC-tech-task-1'
    random_num = random.randint(100000, 1000000)
    git_url = "https://github.com/insidesherpa/%s.git" % (git_dir)
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
            if (len(all_tests) > 0):
                tests_failed = all_tests
            else:
                # Find all fail tests using Regex and return as an array
                find_fails = re.compile('FAIL.*')
                all_fails = find_fails.findall(test_output)
                tests_failed = all_fails
        else:
            tests_failed = ['FAIL. Failed to apply patch']

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
    # DEVELOPER TO-DO: Place your patch file to test in the downloadLoc path
    # This assumes / simulates we've already downloaded the file from S3
    downloadLoc = '/tmp/test_file.patch'
 
    if os.path.isfile(downloadLoc):
        # Run tests and store failed results as array
        failed_tests = run_tests(downloadLoc)
    else:
        failed_tests = ['failed downloading patch file']

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
