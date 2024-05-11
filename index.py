import json


def handler(event, context):
    print(f"Event received: {event}")
    return {"statusCode": 200, "body": json.dumps({"message": "Hello World!"})}
