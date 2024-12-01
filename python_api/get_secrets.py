import boto3
from botocore.exceptions import ClientError
import json


def get_secret_rapid_api():
    secret_name = "Rapid_API_auth_token"
    region_name = "eu-north-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']

    return secret


rapid_api_credentials = get_secret_rapid_api()

json_parameters = rapid_api_credentials.replace("'", "\"")

parameters = json.loads(json_parameters)

rapid_api_key = parameters['Rapid Auth Token']

foul_bot = parameters['Foul Bot Token']

gold_channel = parameters['Group Id']

gpt_key = parameters['GPT4 Key']


def get_secret_db():

    secret_name = "shaddy_powder_db"
    region_name = "eu-north-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']
    
    return secret

db_credentials = get_secret_db()

db_json_parameters = db_credentials.replace("'", "\"")

db_parameters = json.loads(db_json_parameters)

# print(db_parameters)

# print(rapid_api_key)

