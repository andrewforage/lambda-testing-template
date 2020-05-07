from flask import jsonify

import boto3
import json
import os
import requests

# LAMBDA_API_KEY = 'testing'
#SESSION = boto3.Session(
#   aws_access_key_id='<not_needed>',
#    aws_secret_access_key='<not_needed'

#S3 = SESSION.resource('s3')

# Download the file from S3 and save into /tmp
# This is disabled.
# You will not need this when making your own test locally
#def download_file(fileUrl, uId, mId):
#    try:
#        fileUrl = fileUrl.replace('https://<some_s3_bucket>', '')
#        fileExtension = fileUrl.split('.')[-1]
#        fileLocation = '/tmp/%s_%s.%s' % (uId, mId, fileExtension)
#        S3.Bucket('<some_s3_bucket>').download_file(fileUrl, fileLocation)
#    except Exception as e:
#        print(e)
#        fileLocation = False
#    return fileLocation

def validate_request(request):
    # Check headers
    requestData = request.json
    if not ('Content-Type' in request.headers
            and request.headers['Content-Type'] == 'application/json'):
        return False

    # Check correct data was passed
    if not ('key' in requestData and requestData['key'] == LAMBDA_API_KEY):
        return False

    if not ('moduleId' in requestData and 'deliverableId' in requestData
            and 'userId' in requestData and 'fileUrl' in requestData
            and 'submissionKey' in requestData and 'skillId' in requestData
            and 'timeCalled' in requestData):
        return False

    if not ('callbackUrl' in requestData):
        return False
    return True

def mark(deliverable, execTests, ancilliaryInfo):
    # Download the deliverable
    # DEVELOPER TO-DO: Place your document file (e.g. pptx)
    # to test in the downloadLoc path
    # This assumes / simulates we've already downloaded the file from S3
    downloadLoc = '/tmp/test.pptx'

    if (downloadLoc != False):
        # Run tests and store failed results as array
        testsFailed = execTests(downloadLoc, ancilliaryInfo)
        # Delete file from system after marked
        # TIP: You can comment this out so you retain the doc in your pc
        os.remove(downloadLoc)
    else:
        testsFailed = ['failed downloading file']

    # Fire callback to callback URL
    callback = {
        'marked': True,
        'testsFailed': len(testsFailed),
        'testResults': testsFailed,
        'deliverableId': deliverable['deliverableId'],
        'autoMarkingTestId': deliverable['autoMarkingTestId'],
        'userId': deliverable['userId'],
        'submissionKey': deliverable['submissionKey'],
        'timeCalled': deliverable['timeCalled'],
        'skillId': deliverable['skillId'],
        'moduleId': deliverable['moduleId'],
        # 'key': LAMBDA_API_KEY,
    }

    print('Beginning callback to %s' % deliverable['callbackUrl'])
    callbackReq = {}
    try:
        callbackReq = requests.post(url=deliverable['callbackUrl'], headers={
            'content-type': 'application/json'
        }, data=json.dumps(callback))
    except Exception as e:
        print(e)

    if callbackReq:
        print('Status Code: %s' % callbackReq.status_code)
        print('Response:')
        print(callbackReq.content)

def begin_test(request, marker):
    """
    LOGIC: 
    1. Receives JSON Post request
    2. Downloads response from S3
    3. Runs tests
    4. Returns JSON response of successful tests
    """
    if request.method == 'POST':
        deliverable = request.json
        if not validate_request(request):
            return jsonify({'error': 'invalid parameters provided'})

        marker(deliverable)

        return jsonify({
            'success': True,
            'message': ('[start] marking deliverableId: %s' %
            deliverable['deliverableId'])
        })

    return jsonify({'error': 'invalid parameters provided'})