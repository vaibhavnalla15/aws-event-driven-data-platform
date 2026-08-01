from datetime import datetime, timezone
from decimal import Decimal
import boto3
import csv
import io
import json

# ==========================================================
# AWS Clients
# ==========================================================

s3 = boto3.client("s3")
sqs = boto3.client("sqs")
dynamodb = boto3.resource("dynamodb")

processing_table = dynamodb.Table("enterprise-processing-metadata")

customer_table = dynamodb.Table("enterprise-customers")

# ==========================================================
# Retry Configuration
# ==========================================================

MAX_RETRIES = 3

DLQ_URL = "https://sqs.us-east-1.amazonaws.com/321869098112/enterprise-processing-dlq"

def lambda_handler(event, context):

    print("========== SQS EVENT RECEIVED ==========")
    print(json.dumps(event, indent=2))

    # --------------------------------------------------
    # Process each SQS Message
    # --------------------------------------------------

    for record in event["Records"]:

        # --------------------------------------------------
        # Read SQS Message
        # --------------------------------------------------

        message = json.loads(record["body"])

        bucket_name = message["bucket_name"]
        object_key = message["object_key"]
        total_records = message["total_records"]
        invalid_rows = message["invalid_rows"]

        print(f"Bucket Name   : {bucket_name}")
        print(f"Object Key    : {object_key}")
        print(f"Total Records : {total_records}")
        print(f"Invalid Rows  : {invalid_rows}")

        response = processing_table.get_item(
            Key={
                "file_id": object_key
            }
        )

        existing_item = response.get("Item")

        if existing_item and existing_item.get("status") == "COMPLETED":

            print("Duplicate processing request detected.")

            print("File has already been processed.")

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "File already processed. Skipping."
                })
            }

        # --------------------------------------------------
        # Download CSV from S3
        # --------------------------------------------------

        response = s3.get_object(
            Bucket=bucket_name,
            Key=object_key
        )

        content = response["Body"].read().decode("utf-8")

        print("CSV downloaded successfully.")

        # --------------------------------------------------
        # Transform CSV into Customer Objects
        # --------------------------------------------------

        csv_reader = csv.DictReader(io.StringIO(content))
        rows = list(csv_reader)

        print(f"Customer Records Loaded : {len(rows)}")

        if rows:
            print("First Customer Record:")
            print(json.dumps(rows[0], indent=2))
        else:
            print("No customer records found.")

        processing_start_time = datetime.now(timezone.utc).isoformat()

        created_at = processing_start_time
        last_updated_at = processing_start_time    

        # --------------------------------------------------
        # Store Processing Metadata
        # --------------------------------------------------

        processing_table.put_item(
            Item={
                "file_id": object_key,
                "bucket_name": bucket_name,
                "object_key": object_key,

                "total_records": total_records,
                "processed_records": 0,
                "failed_records": 0,

                "status": "PROCESSING",

                "processing_start_time": processing_start_time,

                "created_at": created_at,
                "last_updated_at": last_updated_at
            }
        )

        print("Processing metadata stored in DynamoDB.")

        # --------------------------------------------------
        # Process Customer Records
        # --------------------------------------------------

        print("Starting customer record processing...")

        processed_records = 0
        failed_records = 0

        for index, customer in enumerate(rows, start=1):

            success = False

            for attempt in range(1, MAX_RETRIES + 1):

                try:

                    print(
                        f"Processing Customer {index} "
                        f"(Attempt {attempt}/{MAX_RETRIES})"
                    )

                    # --------------------------------------------------
                    # Future Business Logic
                    # --------------------------------------------------

                    print(json.dumps(customer, indent=2))

                    if customer["Customer ID"] == "CUST-0005":
                        raise Exception("Simulated customer processing failure")

                    customer_table.put_item(
                        Item={
                            "customer_id": customer["Customer ID"],
                            "company_name": customer["Company Name"],
                            "email_primary": customer["Email Primary"],
                            "industry": customer.get("Industry", ""),
                            "country": customer.get("Country", "")
                        }
                    )

                    print(f"Customer {customer['Customer ID']} stored successfully.")

                    processed_records += 1

                    success = True

                    break

                except Exception as e:

                    print(
                        f"Attempt {attempt} failed: {str(e)}"
                    )

            if not success:

                failed_records += 1

                dlq_message = {
                    "file_id": object_key,
                    "customer_number": index,
                    "customer_id": customer.get("Customer ID"),
                    "company_name": customer.get("Company Name"),
                    "email_primary": customer.get("Email Primary"),
                    "error": "Customer processing failed after maximum retry attempts.",
                    "attempts": MAX_RETRIES
                }

                response = sqs.send_message(
                    QueueUrl=DLQ_URL,
                    MessageBody=json.dumps(dlq_message)
                )

                print(f"Customer {customer.get('Customer ID')} sent to DLQ.")

                print(f"DLQ Message ID: {response['MessageId']}")

        print("Customer record processing completed.")

        processing_end_time = datetime.now(timezone.utc).isoformat()

        processing_duration_seconds = Decimal(
            str(
                (
                    datetime.fromisoformat(processing_end_time) -
                    datetime.fromisoformat(processing_start_time)
                ).total_seconds()
            )
        )

        processed_records = len(rows)

        failed_records = 0

        last_updated_at = processing_end_time

        if failed_records == 0:
            processing_status = "COMPLETED"
        else:
            processing_status = "COMPLETED_WITH_ERRORS"

        # --------------------------------------------------
        # Update Processing Status
        # --------------------------------------------------

        processing_table.update_item(
            Key={
                "file_id": object_key
            },
            UpdateExpression="""
                SET
                    #status = :status,
                    processed_records = :processed_records,
                    failed_records = :failed_records,
                    processing_end_time = :processing_end_time,
                    processing_duration_seconds = :processing_duration_seconds,
                    last_updated_at = :last_updated_at
            """,
            ExpressionAttributeNames={
                "#status": "status"
            },
            ExpressionAttributeValues={
                ":status": processing_status,
                ":processed_records": processed_records,
                ":failed_records": failed_records,
                ":processing_end_time": processing_end_time,
                ":processing_duration_seconds": processing_duration_seconds,
                ":last_updated_at": last_updated_at
            }
        )

        print("Processing metadata updated successfully.")

        print("Processing status updated to COMPLETED.")

        # --------------------------------------------------
        # Move File to Processed Folder
        # --------------------------------------------------

        processed_key = object_key.replace("incoming/", "processed/", 1)

        s3.copy_object(
            Bucket=bucket_name,
            CopySource={
                "Bucket": bucket_name,
                "Key": object_key
            },
            Key=processed_key
        )

        print(f"File copied to: {processed_key}")

        s3.delete_object(
            Bucket=bucket_name,
            Key=object_key
        )

        print("Original file deleted from incoming/")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Processing completed successfully."
        })
    }