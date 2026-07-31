import json

def lambda_handler(event, context):

    print("========== SQS EVENT RECEIVED ==========")
    print(json.dumps(event, indent=2))

    for record in event["Records"]:

        message = json.loads(record["body"])

        bucket_name = message["bucket_name"]
        object_key = message["object_key"]
        total_records = message["total_records"]
        invalid_rows = message["invalid_rows"]

        print(f"Bucket Name : {bucket_name}")
        print(f"Object Key  : {object_key}")
        print(f"Total Records : {total_records}")
        print(f"Invalid Rows : {invalid_rows}")

    return {
        "statusCode": 200,
        "body": json.dumps("Message processed successfully.")
    }