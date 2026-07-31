import boto3
import csv
import io
import json

s3 = boto3.client("s3")

def lambda_handler(event, context):

    print("========== SQS EVENT RECEIVED ==========")
    print(json.dumps(event, indent=2))

    for record in event["Records"]:

        message = json.loads(record["body"])

        bucket_name = message["bucket_name"]
        object_key = message["object_key"]
        
        response = s3.get_object(
            Bucket=bucket_name,
            Key=object_key
        )

        content = response["Body"].read().decode("utf-8")

        csv_reader = csv.reader(io.StringIO(content))
        rows = list(csv_reader)

        print("CSV downloaded successfully.")
        print(f"Header: {rows[0]}")
        print(f"Total Records: {len(rows) - 1}")

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