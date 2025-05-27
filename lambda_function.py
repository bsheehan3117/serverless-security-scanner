import json
import boto3
from datetime import datetime, timezone

def scan_for_issues(data, file_size=None):
    """
    Scan JSON data for security vulnerabilities.
    Returns a list of found vulnerabilities.
    
    Args:
        data: Parsed JSON content from the file
        file_size: Size of the file in bytes (optional)
    
    Returns:
        List of vulnerability dictionaries
    """
    vulnerabilities = []
    
    # Check for SSL disabled
    # Using data.get() prevents KeyError if 'ssl_enabled' doesn't exist
    if data.get('ssl_enabled') == False:
        vulnerabilities.append({
            "type": "ssl_disabled",
            "severity": "HIGH",
            "field": "ssl_enabled",
            "value": "false",
            "recommendation": "Enable SSL for encrypted connections"
        })
    
    # Check for debug mode enabled
    # Debug mode can expose sensitive information in production
    if data.get('debug_mode') == True:
        vulnerabilities.append({
            "type": "debug_mode_enabled",
            "severity": "MEDIUM",
            "field": "debug_mode",
            "value": "true",
            "recommendation": "Disable debug mode in production"
        })
    
    # Check for hardcoded password
    # Logic: If password exists AND doesn't contain "/" (parameter store reference)
    # then it's likely hardcoded
    if 'database' in data and 'password' in data['database']:
        
        # Convert to string to safely check for "/" character
        if '/' not in str(data['database']['password']):
            vulnerabilities.append({
                "type": "hardcoded_password",
                "severity": "CRITICAL",  
                "field": "database.password",
                "value": "[REDACTED]",  # Never log actual passwords
                "recommendation": "Use AWS Parameter Store or Secrets Manager"
            })
    
    # Check for hardcoded API key using same logic as password
    if 'api_key' in data and '/' not in str(data['api_key']):
        vulnerabilities.append({
            "type": "hardcoded_api_key",
            "severity": "HIGH",
            "field": "api_key",
            "value": "[REDACTED]",
            "recommendation": "Use AWS Parameter Store or Secrets Manager"
        })
    
    # Check for suspiciously large file size
    # 10 MB = 10 * 1024 * 1024 bytes
    if file_size and file_size > 10 * 1024 * 1024:
        vulnerabilities.append({
            "type": "suspicious_file_size",
            "severity": "MEDIUM",
            "field": "file_size",
            "value": f"{file_size} bytes",
            "recommendation": "Review why configuration file is unusually large"
        })
    
    return vulnerabilities

def send_security_alert(bucket_name, object_key, vulnerabilities):
    """
    Format and send security alert for found vulnerabilities.
    For demo, using CloudWatch Logs. In production, would use SNS.
    
    Args:
        bucket_name: S3 bucket where file was found
        object_key: Path/name of the file in S3
        vulnerabilities: List of vulnerability dictionaries from scan_for_issues
    """
    # Skip alert if no vulnerabilities found
    if not vulnerabilities:
        print("No vulnerabilities found - no alert sent")
        return
    
    # Create structured alert message for easy parsing/monitoring
    alert = {
        "alert_type": "SECURITY_SCAN_ALERT",
        # ISO format timestamp with timezone for proper logging
        "timestamp": datetime.now(timezone.utc).isoformat(),

        # Full S3 path for easy file location
        "file_scanned": f"s3://{bucket_name}/{object_key}",
        "vulnerability_count": len(vulnerabilities),
        "vulnerabilities": vulnerabilities,

        # Summary helps with quick severity assessment
        "severity_summary": {

            # List counts vulnerabilities by severity level
            "CRITICAL": len([v for v in vulnerabilities if v['severity'] == 'CRITICAL']),
            "HIGH": len([v for v in vulnerabilities if v['severity'] == 'HIGH']),
            "MEDIUM": len([v for v in vulnerabilities if v['severity'] == 'MEDIUM'])
        }
    }
    
    # Log the alert (in production, this would go to SNS)
    print(" SECURITY ALERT ")
    print(json.dumps(alert, indent=2))
    
    return alert

def lambda_handler(event, context):
    """
    Main entry point for Lambda function.
    AWS Lambda always calls this specific function name.
    
    Args:
        event: Contains S3 event data (bucket, object key, etc.)
        context: Lambda runtime information (timeout, request ID, etc.)
    
    Returns:
        Dict with statusCode and body
    """
    print("Received event:", json.dumps(event))

    try:
        # Parse S3 event structure
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        object_key = event['Records'][0]['s3']['object']['key']

        print(f"Processing file: {object_key} from bucket: {bucket_name}")

        # Pre-check file extension to avoid downloading unnecessary files
        # skip if not a JSON file, still successful execution
        if not object_key.endswith('.json'):
            print(f"Skipping non-JSON file: {object_key}")
            return {
                'statusCode': 200,  
                'body': json.dumps('Non-JSON file skipped')
            }
        
        # Initialize S3 client and read the file
        s3_client = boto3.client('s3')

        # get_object downloads file content from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response['Body'].read().decode('utf-8')
        file_size = response['ContentLength']
        
        print(f"File size: {file_size} bytes")
        
        # Parse JSON content - this could raise ValueError if invalid JSON
        data = json.loads(file_content)          

        # Scan for vulnerabilities and send alert if found
        vulnerabilities = scan_for_issues(data, file_size)
        print(f"Found {len(vulnerabilities)} vulnerabilities")
        alert = send_security_alert(bucket_name, object_key, vulnerabilities)

        return {
            'statusCode': 200,
            'body': json.dumps(f'File processed successfully. Found {len(vulnerabilities)} vulnerabilities.')
        }

    except Exception as e:
        # Catch all exceptions to prevent Lambda from crashing
        print(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,  
            'body': json.dumps(f'Error: {str(e)}')
        }