import json
import boto3

def lambda_handler(event, context):
    """
    Main entry point for Lambda function.
    Triggered by S3 file upload events.
    """
    print("Received event:", json.dumps(event))

    try:
        # Parse the S3 event
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        object_key = event['Records'][0]['s3']['object']['key']

        print(f"Processing file: {object_key} from bucket: {bucket_name}")

        # TODO: Add S3 read logic.
        # Read the file from S3
        # Before reading from s3, check if it is a json file.  Skip it not, do not error.
        # Flag large files as suspicious but do not fail them.
        # Track size issue in the vulnerabilty list to be made available later.
        s3_client = boto3.client('s3')
        if not object_key.endswith('.json'):
            print(f"Skipping non-JSON file: {object_key}")
            return {
                'statusCode': 200,
                'body': json.dumps('Non-JSON file skipped')
            }
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response['Body'].read().decode('utf-8')
        file_size = response['ContentLength']
        print(f"File size: {file_size} bytes")
        if file_size > 10 * 1024 * 1024:  # 10 MB threshold
            print(f"Large file detected: {object_key} ({file_size} bytes)")
            # Flag this file as suspicious, but continue processing it
            # You can log this or add it to a vulnerability list
            print("File size exceeds 10 MB, flagging as suspicious.")
        else:
            print(f"File size is acceptable: {file_size} bytes")  
        data = json.loads(file_content)          

        # TODO: Add vulnerability scanning
        
        # TODO: Add alerting

        return {
            'statusCode': 200,
            'body': json.dumps('File processed successfully')
        }

    except Exception as e:
        print(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
