from urllib.parse import unquote_plus
import re
import json
import boto3
import csv
import io

# AWS Clients
s3 = boto3.client("s3")
sqs = boto3.client("sqs")

QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/321869098112/enterprise-processing-queue"

# ==========================================================
# Required Columns
# ==========================================================

REQUIRED_COLUMNS = [
    "Customer ID",
    "Company Name",
    "Email Primary"
]

# ==========================================================
# Optional Columns
# ==========================================================

OPTIONAL_COLUMNS = [
    "Index",
    "Primary Contact First Name",
    "Primary Contact Last Name",
    "Secondary Contact First Name",
    "Secondary Contact Last Name",
    "Email Secondary",
    "Phone Primary",
    "Phone Secondary",
    "Website",
    "Industry",
    "Company Description",
    "Number of Employees",
    "Annual Revenue",
    "Address",
    "City",
    "Country",
    "Account Manager",
    "Department",
    "Contract Start Date",
    "Contract End Date",
    "Contract Value",
    "Payment Terms",
    "Special Requirements",
    "Support Level",
    "Lead Source",
    "Last Contact Date",
    "Next Follow Up Date",
    "Customer Since",
    "Notes",
    "History",
    "Messages",
    "Implementation Instructions"
]

# ==========================================================
# Email Validation Pattern
# ==========================================================

EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)


def lambda_handler(event, context):
    try:
        print("========== EVENT RECEIVED ==========")
        print(json.dumps(event, indent=2))

        # --------------------------------------------------
        # Get S3 Bucket & Object
        # --------------------------------------------------

        record = event["Records"][0]

        bucket_name = record["s3"]["bucket"]["name"]
        object_key = unquote_plus(record["s3"]["object"]["key"])

        print(f"Bucket Name : {bucket_name}")
        print(f"Object Key  : {object_key}")

        # --------------------------------------------------
        # Download CSV
        # --------------------------------------------------

        response = s3.get_object(
            Bucket=bucket_name,
            Key=object_key
        )

        print("CSV downloaded successfully.")

        # --------------------------------------------------
        # Read CSV
        # --------------------------------------------------

        content = response["Body"].read().decode("utf-8")

        csv_reader = csv.reader(io.StringIO(content))
        rows = list(csv_reader)

        if not rows:
            raise ValueError("Uploaded CSV is empty.")

        header = rows[0]
        total_records = len(rows) - 1

        print(f"Header : {header}")
        print(f"Total Records : {total_records}")

        # --------------------------------------------------
        # Hybrid Schema Validation
        # --------------------------------------------------

        missing_columns = [
            column
            for column in REQUIRED_COLUMNS
            if column not in header
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {', '.join(missing_columns)}"
            )

        print("Required columns validation passed.")

        available_optional_columns = [
            column
            for column in OPTIONAL_COLUMNS
            if column in header
        ]

        print(
            f"Optional columns found: {len(available_optional_columns)}"
        )

        print("CSV schema validation completed successfully.")

        # --------------------------------------------------
        # Row-Level Validation
        # --------------------------------------------------

        print("Starting row-level validation...")

        required_column_indexes = {
            column: header.index(column)
            for column in REQUIRED_COLUMNS
        }

        email_index = required_column_indexes["Email Primary"]

        invalid_rows = []

        seen_customer_ids = set()

        for row_number, row in enumerate(rows[1:], start=2):

            # Skip completely empty rows
            if not any(cell.strip() for cell in row):
                continue

            row_errors = []

            # ----------------------------------------------
            # Required Field Validation
            # ----------------------------------------------

            for column, index in required_column_indexes.items():

                value = ""

                if index < len(row):
                    value = row[index].strip()

                if value == "":
                    row_errors.append(f"Missing {column}")

            # ----------------------------------------------
            # Email Format Validation
            # ----------------------------------------------

            if email_index < len(row):

                email = row[email_index].strip()

                if email and not EMAIL_PATTERN.match(email):
                    row_errors.append("Invalid Email Format")

            # ----------------------------------------------
            # Duplicate Customer ID Validation
            # ----------------------------------------------

            customer_id_index = required_column_indexes["Customer ID"]

            if customer_id_index < len(row):

                customer_id = row[customer_id_index].strip()

                if customer_id:

                    if customer_id in seen_customer_ids:
                        row_errors.append("Duplicate Customer ID")
                    else:
                        seen_customer_ids.add(customer_id)        

            # ----------------------------------------------
            # Save Validation Errors
            # ----------------------------------------------

            if row_errors:
                invalid_rows.append(
                    {
                        "row": row_number,
                        "errors": row_errors
                    }
                )

        # --------------------------------------------------
        # Validation Summary
        # --------------------------------------------------

        print(f"Invalid Rows: {len(invalid_rows)}")

        for item in invalid_rows:
            print(
                f"Row {item['row']} Errors: {', '.join(item['errors'])}"
            )

        message = {
        "bucket_name": bucket_name,
        "object_key": object_key,
        "total_records": total_records,
        "invalid_rows": len(invalid_rows)
        }    

        response = sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(message)
        )

        print("Metadata successfully sent to SQS.")
        print(f"Message ID: {response['MessageId']}")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "CSV validation completed successfully.",
                "total_records": total_records,
                "invalid_rows": len(invalid_rows)
            })
        }

    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise