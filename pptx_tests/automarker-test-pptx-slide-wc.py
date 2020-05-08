from flask import Flask, jsonify, request
from pptx import Presentation
from zappa.asynchronous import task

import common
import os
import pptxHelper as helper
import requests
import sys

# Configuration and declaration
app = Flask(__name__)
# LAMBDA_API_KEY = 'testing'
###################################################
# You should not need to edit any of the code above

# Runs tests
# DEVELOPER TO-DO: This is where you will write your test
# Feel free to override the current test...
def run_tests(fileLocation, slideWCTestInfo):
    # DEVELOPER NOTES: This testsFailed array determines if a file passes a test
    # If it is returned as empty then a file is deemed to have passed the test
    # Else, the file fails to meet the criteria of the test...
    testsFailed = []
    path = str(fileLocation)

    #ensure cwd is in /tmp chdir
    os.chdir('/tmp')

    if (path.endswith('.pptx') == False):
        return ['FAIL: wrong file extension']
    
    try:
        prs = Presentation(path)

        # Initial variables
        slideWCMin = helper.DEFAULT_S_WC_MIN if 'wcMin' not in slideWCTestInfo else slideWCTestInfo['wcMin']
        slideWCMax = helper.DEFAULT_S_WC_MAX if 'wcMax' not in slideWCTestInfo else slideWCTestInfo['wcMax']
        slideNumber = 1 if 'slideNumber' not in slideWCTestInfo else slideWCTestInfo['slideNumber']

        print("Starting Test")
        print(slideWCTestInfo)

        elements = helper.getTextElements(prs, slideNumber, [])
        if 'invalid' in elements:
            print(elements['invalid'])
            return elements['invalid']
        totalWC = 0
        for text in elements['texts']:
            totalWC += len(text.split(' '))
            print("slideNumber({}) - text: {}".format(slideNumber, text))
        
        if totalWC > slideWCMax:
            testsFailed.append(["FAIL: slide word count exceeded len({}), max({}), slideNumber({})".format(totalWC, slideWCMax, slideNumber)])
        elif totalWC < slideWCMin:
            testsFailed.append(["FAIL: slide word count too few len({}), min({}), slideNumber({})".format(totalWC, slideWCMin, slideNumber)])
        else:
            print("Passed: slideNumber({}) - word count({})".format(slideNumber, totalWC))
        print(testsFailed)
            
    except Exception as e:
        print(e)
        testsFailed = ['FAIL: Something went wrong with parsing the pptx']

    return testsFailed



# Run async marking asynchronously
@task
def handle_async_marking(deliverable):
    # DEVELOPER TO-DO: This is where this endpoint extracts
    # meta data / parameters / arguments for the test
    # This test checks word count but a good word count can
    # be adjusted with a max and min count that we pass inside
    # the request to run this test
    # Feel free to override this part depending on the test you will write
    generalInfo = {} if 'generalAutoTestingInfo' not in deliverable else deliverable['generalAutoTestingInfo']
    slideWCTestInfo = {} if 'slideWCTest' not in generalInfo else generalInfo['slideWCTest']
    common.mark(deliverable, run_tests, slideWCTestInfo)


# You should not need to edit any code below
############################################
@app.route('/test', methods=['GET', 'POST'])
def begin_test():
   return common.begin_test(request, handle_async_marking)

if __name__ == '__main__':
    app.run(debug=True)
