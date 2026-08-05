from datetime import datetime, timezone
from decimal import Decimal

import csv
import io
import json
import os
import boto3

# ==========================================================
# AWS Clients
# ==========================================================

s3 = boto3.client("s3")
sqs = boto3.client("sqs")
dynamodb = boto3.resource("dynamodb")

# ==========================================================
# DynamoDB Tables
# ==========================================================

processing_table = dynamodb.Table(
    os.environ["PROCESSING_METADATA_TABLE"]
)

customer_table = dynamodb.Table(
    os.environ["CUSTOMERS_TABLE"]
)

# ==========================================================
# Configuration
# ==========================================================

MAX_RETRIES = 3

DLQ_URL = os.environ["DLQ_URL"]

PROCESSED_PREFIX = "processed/"
INCOMING_PREFIX = "incoming/"

# ==========================================================
# Helper Functions
# ==========================================================

def current_timestamp():
    """
    Returns current UTC timestamp in ISO-8601 format.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()


def download_csv(bucket_name, object_key):
    """
    Downloads CSV from Amazon S3 and
    returns customer records.
    """

    print("Downloading CSV from Amazon S3...")

    response = s3.get_object(
        Bucket=bucket_name,
        Key=object_key
    )

    content = (
        response["Body"]
        .read()
        .decode("utf-8")
    )

    csv_reader = csv.DictReader(
        io.StringIO(content)
    )

    rows = list(csv_reader)

    print(
        f"CSV downloaded successfully "
        f"({len(rows)} records)"
    )

    return rows


def check_duplicate_processing(object_key):
    """
    Checks whether the file
    has already been processed.
    """

    response = processing_table.get_item(
        Key={
            "file_id": object_key
        }
    )

    item = response.get("Item")

    if (
        item
        and item.get("status")
        in [
            "COMPLETED",
            "COMPLETED_WITH_ERRORS"
        ]
    ):

        print("=" * 60)
        print("Duplicate processing detected.")
        print("Skipping file.")
        print("=" * 60)

        return True

    return False


def store_processing_metadata(
    bucket_name,
    object_key,
    total_records,
    processing_start_time
):
    """
    Creates initial processing metadata.
    """

    processing_table.put_item(

        Item={

            "file_id": object_key,

            "bucket_name": bucket_name,

            "object_key": object_key,

            "total_records": total_records,

            "processed_records": 0,

            "failed_records": 0,

            "status": "PROCESSING",

            "processing_start_time":
                processing_start_time,

            "created_at":
                processing_start_time,

            "last_updated_at":
                processing_start_time

        }

    )

    print(
        "Processing metadata created."
    )


def send_to_dlq(
    object_key,
    customer_number,
    customer
):
    """
    Sends permanently failed
    customer record to DLQ.
    """

    message = {

        "file_id":
            object_key,

        "customer_number":
            customer_number,

        "customer_id":
            customer.get("Customer ID"),

        "company_name":
            customer.get("Company Name"),

        "email_primary":
            customer.get("Email Primary"),

        "error":
            (
                "Customer processing "
                "failed after maximum "
                "retry attempts."
            ),

        "attempts":
            MAX_RETRIES

    }

    response = sqs.send_message(

        QueueUrl=DLQ_URL,

        MessageBody=json.dumps(message)

    )

    print(
        f"Customer "
        f"{customer.get('Customer ID')} "
        f"sent to DLQ."
    )

    print(
        f"DLQ Message ID: "
        f"{response['MessageId']}"
    )

def update_processing_metadata(
    object_key,
    processed_records,
    failed_records,
    processing_start_time
):
    """
    Updates processing metadata after
    customer processing completes.
    """

    processing_end_time = current_timestamp()

    processing_duration_seconds = Decimal(
        str(
            (
                datetime.fromisoformat(processing_end_time)
                -
                datetime.fromisoformat(processing_start_time)
            ).total_seconds()
        )
    )

    if failed_records == 0:
        processing_status = "COMPLETED"
    else:
        processing_status = "COMPLETED_WITH_ERRORS"

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

            ":status":
                processing_status,

            ":processed_records":
                processed_records,

            ":failed_records":
                failed_records,

            ":processing_end_time":
                processing_end_time,

            ":processing_duration_seconds":
                processing_duration_seconds,

            ":last_updated_at":
                processing_end_time

        }

    )

    print("=" * 60)
    print("Processing metadata updated.")
    print(f"Status            : {processing_status}")
    print(f"Processed Records : {processed_records}")
    print(f"Failed Records    : {failed_records}")
    print(
        f"Duration (sec)    : "
        f"{processing_duration_seconds}"
    )
    print("=" * 60)


def move_to_processed_folder(
    bucket_name,
    object_key
):
    """
    Moves processed file from
    incoming/ to processed/.
    """

    processed_key = object_key.replace(
        INCOMING_PREFIX,
        PROCESSED_PREFIX,
        1
    )

    s3.copy_object(

        Bucket=bucket_name,

        CopySource={
            "Bucket": bucket_name,
            "Key": object_key
        },

        Key=processed_key

    )

    print(
        f"Copied to: {processed_key}"
    )

    s3.delete_object(

        Bucket=bucket_name,

        Key=object_key

    )

    print(
        "Original file deleted "
        "from incoming/."
    )


# ==========================================================
# Lambda Handler
# ==========================================================

def lambda_handler(event, context):

    print("=" * 70)
    print("PROCESSING LAMBDA STARTED")
    print("=" * 70)

    print(json.dumps(event, indent=2))

    for record in event["Records"]:

        # --------------------------------------------------
        # Read SQS Message
        # --------------------------------------------------

        message = json.loads(
            record["body"]
        )

        bucket_name = message["bucket_name"]
        object_key = message["object_key"]
        total_records = message["total_records"]
        invalid_rows = message["invalid_rows"]

        print("=" * 60)
        print("FILE INFORMATION")
        print("=" * 60)

        print(f"Bucket Name   : {bucket_name}")
        print(f"Object Key    : {object_key}")
        print(f"Total Records : {total_records}")
        print(f"Invalid Rows  : {invalid_rows}")

        # --------------------------------------------------
        # Idempotency Check
        # --------------------------------------------------

        if check_duplicate_processing(
            object_key
        ):

            continue

        # --------------------------------------------------
        # Download CSV
        # --------------------------------------------------

        rows = download_csv(
            bucket_name,
            object_key
        )

        if rows:

            print("=" * 60)
            print("FIRST CUSTOMER")
            print("=" * 60)

            print(
                json.dumps(
                    rows[0],
                    indent=2
                )
            )

        else:

            print(
                "No customer "
                "records found."
            )

        processing_start_time = (
            current_timestamp()
        )

        # --------------------------------------------------
        # Store Initial Metadata
        # --------------------------------------------------

        store_processing_metadata(

            bucket_name=bucket_name,

            object_key=object_key,

            total_records=total_records,

            processing_start_time=
                processing_start_time

        )

        print("=" * 60)
        print("Customer Processing Started")
        print("=" * 60)

        processed_records = 0
        failed_records = 0

        # --------------------------------------------------
        # Process Customer Records
        # --------------------------------------------------

        for index, customer in enumerate(
            rows,
            start=1
        ):

            print("-" * 60)

            print(
                f"Customer {index} of "
                f"{len(rows)}"
            )

            success = False

            # ----------------------------------------------
            # Retry Strategy
            # ----------------------------------------------

            for attempt in range(
                1,
                MAX_RETRIES + 1
            ):

                try:

                    print(
                        f"Attempt "
                        f"{attempt}/"
                        f"{MAX_RETRIES}"
                    )

                    # --------------------------------------
                    # Store Customer
                    # --------------------------------------

                    customer_table.put_item(

                        Item={

                            "customer_id":
                                customer["Customer ID"],

                            "company_name":
                                customer["Company Name"],

                            "email_primary":
                                customer["Email Primary"],

                            "industry":
                                customer.get(
                                    "Industry",
                                    ""
                                ),

                            "country":
                                customer.get(
                                    "Country",
                                    ""
                                )

                        }

                    )

                    print(

                        f"Customer "

                        f"{customer['Customer ID']} "

                        f"stored successfully."

                    )

                    processed_records += 1

                    success = True

                    break

                except Exception as e:

                    print(

                        f"Attempt "

                        f"{attempt} "

                        f"failed."

                    )

                    print(

                        f"Reason: "

                        f"{str(e)}"

                    )

            # ----------------------------------------------
            # All Retries Failed
            # ----------------------------------------------

            if not success:

                failed_records += 1

                send_to_dlq(

                    object_key=object_key,

                    customer_number=index,

                    customer=customer

                )

        print("=" * 60)
        print("Customer Processing Completed")
        print("=" * 60)

        print(
            f"Processed Records : "
            f"{processed_records}"
        )

        print(
            f"Failed Records    : "
            f"{failed_records}"
        )

        # --------------------------------------------------
        # Update Processing Metadata
        # --------------------------------------------------

        update_processing_metadata(

            object_key=object_key,

            processed_records=
                processed_records,

            failed_records=
                failed_records,

            processing_start_time=
                processing_start_time

        )

        # --------------------------------------------------
        # Move File to Processed Folder
        # --------------------------------------------------

        move_to_processed_folder(

            bucket_name=bucket_name,

            object_key=object_key

        )

        print("=" * 60)
        print("FILE PROCESSING COMPLETED")
        print("=" * 60)

        print(f"File              : {object_key}")
        print(f"Processed Records : {processed_records}")
        print(f"Failed Records    : {failed_records}")

        if failed_records == 0:

            print("Overall Status    : SUCCESS")

        else:

            print(
                "Overall Status    : "
                "COMPLETED WITH ERRORS"
            )

        print("=" * 60)

    print("=" * 70)
    print("PROCESSING LAMBDA FINISHED")
    print("=" * 70)

    return {

        "statusCode": 200,

        "body": json.dumps(

            {

                "message":
                    "Processing completed successfully.",

                "status":
                    "SUCCESS"

            }

        )

    }