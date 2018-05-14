import boto3
import json
import urllib.parse
import requests

ROLE_ARN = 'arn:aws:iam::<ACCOUNT_ID>:role/VijayTestRole'
ROLE_SESSION_NAME = 'VijayTestAssumeRole'
SESSION_DURATION = 1800
AWS_FEDERATION_URL = 'https://signin.aws.amazon.com/federation'
#After session timeout, users will be redirected to this url.
ISSUER_URL = 'vastech.com'
AWS_CONSOLE_URL = 'https://console.aws.amazon.com/'

def get_sts_details():
    '''
        This method returns sts_details json object which contains STS temp user 'access key','secret key' and 'session token' details.
    :return: sts_details
    '''
    client = boto3.client('sts')
    response = client.assume_role(
                RoleArn = ROLE_ARN,
                RoleSessionName = ROLE_SESSION_NAME
            )
    #print("Response : ", response)
    print_value("Response", response)

    sts_response_data = {}
    sts_response_data['sessionId'] = response['Credentials']['AccessKeyId']
    sts_response_data['sessionKey'] = response['Credentials']['SecretAccessKey']
    sts_response_data['sessionToken'] = response['Credentials']['SessionToken']
    sts_details = json.dumps(sts_response_data)
    #print("STS_DETAILS : {sts_details}".format(sts_details=sts_details))
    print_value("STS_DETAILS",sts_details)

    return sts_details

def encode_value(value):
    '''
    :param value: Value to be encoded
    :return: returns encoded value.
    '''
    return urllib.parse.quote_plus(value)

def get_aws_federation_request_url(encoded_session_query_parameter):
    '''
        This method returns AWS Federated URL.
    :param encoded_session_query_parameter:
    :return: AWS federated url.
    '''
    request_parameters = "?Action=getSigninToken"
    request_parameters += "&SessionDuration={session_duration}".format(session_duration=SESSION_DURATION)
    request_parameters += "&Session=" + encoded_session_query_parameter
    federation_request_url = AWS_FEDERATION_URL + request_parameters
    #print("federation_request_url : ", federation_request_url)
    print_value("federation_request_url",federation_request_url)
    return federation_request_url

def get_signin_token(federation_request_url):
    '''
        This method returns signin token value.
    :param federation_request_url:
    :return: signin token value
    '''
    response = requests.get(federation_request_url)
    signin_token = json.loads(response.text)['SigninToken']
    #print("signin_token : ", signin_token)
    print_value("signin_token",signin_token)
    return signin_token

def get_aws_signin_url(signin_token):
    '''
        Returns AWS Signin URL
    :param signin_token:
    :return: AWS signin url
    '''
    request_parameters = "?Action=login"
    request_parameters += "&Issuer={issuer_url}".format(issuer_url=ISSUER_URL)
    request_parameters += "&Destination=" + encode_value(AWS_CONSOLE_URL)
    request_parameters += "&SigninToken=" + signin_token
    aws_signin_url = AWS_FEDERATION_URL + request_parameters
    #print("AWS Sign In URL : ", aws_signin_url)
    #print_value("aws_signin_url",aws_signin_url)
    return aws_signin_url

def print_value(name, value):
    print("{name} : {value}\n".format(name=name, value=value))

sts_details = get_sts_details()
encoded_session_query_parameter = encode_value(sts_details)
print("encoded_session_query_parameter : ", encoded_session_query_parameter)

federation_request_url = get_aws_federation_request_url(encoded_session_query_parameter)
signin_token = get_signin_token(federation_request_url)
aws_signin_url = get_aws_signin_url(signin_token)

#print("AWS Signin URL : {aws_signin_url}".format(aws_signin_url=aws_signin_url))
print_value("AWS Signin URL",aws_signin_url)
