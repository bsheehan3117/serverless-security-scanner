import json
from lambda_function import lambda_handler

# Load test event
with open('test_events/sample_s3_event.json', 'r') as f:
    test_event = json.load(f)

# Mock context object
class Context:
    aws_request_id = "test-request-123"

# Test the Lambda
result = lambda_handler(test_event, Context())
print("\n=== Lambda Response ===")
print(json.dumps(result, indent=2))
