import json
import boto3
import csv
import io

# AWS Clients
s3 = boto3.client("s3")

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


def lambda_handler(event, context):
    try:
        print("========== EVENT RECEIVED ==========")
        print(json.dumps(event, indent=2))

        # --------------------------------------------------
        # Get S3 Bucket & Object
        # --------------------------------------------------

        record = event["Records"][0]

        bucket_name = record["s3"]["bucket"]["name"]
        object_key = record["s3"]["object"]["key"]

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

        # Empty file validation
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

        # Optional Columns Information

        available_optional_columns = [
            column
            for column in OPTIONAL_COLUMNS
            if column in header
        ]

        print(
            f"Optional columns found: {len(available_optional_columns)}"
        )

        print("CSV schema validation completed successfully.")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "CSV validation successful.",
                "total_records": total_records
            })
        }

    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise