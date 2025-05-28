# Serverless Security Scanner

An AWS Lambda-based security scanner that automatically detects vulnerabilities in configuration files uploaded to S3. This project explores serverless architecture and cloud security automation using AWS services.  Current scope limited to json files, easily extensible.

## Simple Explanation

Think of this security scanner as an automated security guard for your S3 bucket:

1. **You upload a config file** → S3 bucket receives it
2. **S3 alerts Lambda** → "New file arrived"
3. **Lambda wakes up** → Downloads and reads the file
4. **Security check** → Scans for passwords, weak settings, etc.
5. **Alert generated** → Creates report of any problems found
6. **Results logged** → Saves findings to CloudWatch
7. **Lambda sleeps** → Waits for next file

The beauty: No servers to manage, runs only when needed, costs almost nothing!

## Architecture
S3 Bucket → S3 Event Trigger → Lambda Function → CloudWatch Logs
↓
Vulnerability Scanner
↓
Security Alerts

## Features

- **Automated Scanning**: Triggers automatically when JSON files are uploaded to S3
- **Vulnerability Detection**:
  - Hardcoded passwords and API keys
  - SSL/TLS misconfigurations
  - Debug mode detection
  - Suspicious file size analysis
- **Severity Classification**: CRITICAL, HIGH, MEDIUM
- **Detailed Alerts**: Comprehensive security alerts with remediation recommendations
- **Serverless Architecture**: Cost-effective, scales automatically

## Technologies Used

- **AWS Lambda** (Python 3.9)
- **Amazon S3** (Event triggers)
- **CloudWatch Logs** (Alert delivery)
- **IAM** (Least-privilege security)
- **boto3** (AWS SDK for Python)

## Setup Instructions

### Prerequisites
- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Python 3.9 or higher
- Git

### Step-by-Step Deployment

#### 1. Clone the Repository

```bash
- git clone https://github.com/bsheehan3117/serverless-security-scanner.git
cd serverless-security-scanner

2. Set Up Local Environment

- bashpython3 -m venv venv
- source venv/bin/activate  # On Windows: venv\Scripts\activate
- pip install boto3
- pip freeze > requirements.txt

3. Create S3 Bucket

- bashaws s3 mb s3://security-scanner-bucket-[your-unique-name]
- aws s3api put-bucket-versioning --bucket security-scanner-bucket-[your-unique-name] --versioning-configuration Status=Enabled

4. Create IAM Role for Lambda

Navigate to IAM → Roles → Create role
Select "Lambda" as the trusted entity
Attach AWSLambdaBasicExecutionRole policy
Name it lambda-security-scanner-role
Add inline policy for S3 read access to your bucket

5. Create Lambda Function

Navigate to Lambda → Create function
Function name: serverless-security-scanner
Runtime: Python 3.9
Use existing role: lambda-security-scanner-role
Create function

6. Deploy Code

- bashzip lambda-deployment.zip lambda_function.py
- aws lambda update-function-code --function-name serverless-security-scanner --zip-file fileb://lambda-deployment.zip

7. Configure S3 Trigger

In Lambda console → Configuration → Triggers
Add trigger → S3
Select your bucket
Event type: All object create events
Suffix: .json
Add trigger

8. Test the Scanner

- bashaws s3 cp sample_files/vulnerable_config.json s3://security-scanner-bucket-[your-unique-name]/test/
- aws s3 cp sample_files/secure_config.json s3://security-scanner-bucket-[your-unique-name]/test/
- View results in CloudWatch Logs via Lambda console → Monitor tab

How It Works

File Upload: User uploads a JSON configuration file to S3
Event Trigger: S3 automatically triggers the Lambda function
Vulnerability Scan: Lambda analyzes the configuration for security issues
Alert Generation: Creates detailed alerts with remediation recommendations
Logging: Sends formatted alerts to CloudWatch Logs

Vulnerability Detection
The scanner checks for:

Hardcoded Secrets: Passwords and API keys stored directly in config files
SSL/TLS Issues: Disabled encryption settings
Debug Mode: Production systems with debug enabled
File Size Anomalies: Unusually large configuration files

Test Files
The repository includes sample configuration files in the sample_files/ directory:

vulnerable_config.json - Contains multiple security issues
secure_config.json - Properly configured with no vulnerabilities
partial_vulnerable_config.json - Mixed security posture

Extension Possibilities
This project can be extended to include:

SNS Integration for email/SMS alerts
Additional File Types (YAML, XML, .env)
More Security Checks (weak encryption, public access, outdated protocols)
Container Scanning for Docker configurations
CloudWatch Metrics for vulnerability trending
Third-party Integrations (Jira, Slack, Security Hub)
Machine Learning for anomaly detection

What I Learned
Building this project provided hands-on experience with:

Serverless Architecture: Understanding event-driven computing and its benefits
AWS Service Integration: How Lambda, S3, and CloudWatch work together
Security Automation: Implementing proactive security scanning in cloud environments
Infrastructure as Code: Managing cloud resources programmatically
Cost Optimization: Leveraging serverless for efficient resource usage

Performance

Execution Time: ~2.8 seconds per file
Memory Usage: 89MB (128MB allocated)
Cost: Approximately $0.0000002 per scan
Scalability: Handles concurrent uploads automatically

Security Best Practices

Least-privilege IAM permissions
Sensitive data redaction in logs
No hardcoded credentials
Encrypted data transfer (TLS)
Audit trail via CloudWatch

Troubleshooting
Lambda not triggering:

Verify S3 event notification configuration
Check Lambda permissions
Ensure correct file suffix (.json)

Permission errors:

Verify IAM role has S3:GetObject permission
Check bucket name consistency
Confirm Lambda execution role attachment

JSON parsing errors:

Ensure valid JSON format (no comments)
Check UTF-8 encoding
Verify file isn't corrupted

Author
Brendan Sheehan

GitHub: @bsheehan3117
LinkedIn: https://www.linkedin.com/in/brendansheehan3117/

Exploring serverless security automation in AWS