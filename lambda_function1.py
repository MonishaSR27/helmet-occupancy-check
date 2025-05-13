import boto3
import json
import urllib.parse
from datetime import datetime

def lambda_handler(event, context):
    # Initialize AWS clients
    rekognition_client = boto3.client('rekognition')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('vehicleOccupancyCheck')  # Replace with your table name

    # Extract bucket and object key from S3 event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])

    try:
        # Detect labels in the image
        response = rekognition_client.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': object_key
                }
            },
            MaxLabels=20,
            MinConfidence=60
        )

        labels = response['Labels']

        people_count = 0
        helmet_count = 0

        for label in labels:
            if label['Name'] == 'Person':
                people_count = len(label['Instances'])
            elif 'Helmet' in label['Name']:
                helmet_count += len(label['Instances'])

        # Helmet usage status
        if people_count == 0:
            helmet_status = "No people detected"
        elif helmet_count >= people_count:
            helmet_status = "All people are wearing helmets"
        else:
            not_wearing = people_count - helmet_count
            helmet_status = f"{not_wearing} person(s) not wearing helmet"

        # Updated rule enforcement logic
        if people_count > 2:
            violation = "Violated the rules"
        elif people_count == 2 and helmet_count < 2:
            violation = "Violated the rules"
        else:
            violation = "No violation"

        # Store to DynamoDB
        table.put_item(
            Item={
                'ImageName': object_key,
                'PeopleCount': people_count,
                'HelmetCount': helmet_count,
                'HelmetStatus': helmet_status,
                'RuleStatus': violation,
                'Timestamp': datetime.utcnow().isoformat()
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Helmet and occupancy check complete',
                'PeopleCount': people_count,
                'HelmetCount': helmet_count,
                'HelmetStatus': helmet_status,
                'RuleStatus': violation
            })
        }

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps('Error processing image')
        }