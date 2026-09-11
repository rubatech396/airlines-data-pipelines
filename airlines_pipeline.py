import pandas as pd
import os

folder = "/Users/rubasri/Downloads/UseCase - Airlines 1"

bookings = pd.read_csv(os.path.join(folder, "bookings-Table 1.csv"))
flights = pd.read_csv(os.path.join(folder, "flights-Table 1.csv"))
passengers = pd.read_csv(os.path.join(folder, "passengers-Table 1.csv"))
payments = pd.read_csv(os.path.join(folder, "payments-Table 1.csv"))

print("BOOKINGS")
print(bookings.shape)
print(bookings.columns.tolist())

print("\nFLIGHTS")
print(flights.shape)
print(flights.columns.tolist())

print("\nPASSENGERS")
print(passengers.shape)
print(passengers.columns.tolist())

print("\nPAYMENTS")
print(payments.shape)
print(payments.columns.tolist())

# STEP 6: DATA VALIDATION

print("\n========== DATA VALIDATION ==========")

tables = {
    "Bookings": bookings,
    "Flights": flights,
    "Passengers": passengers,
    "Payments": payments
}

for name, df in tables.items():
    print("\n---", name, "---")

    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    print("Missing values:")
    print(df.isnull().sum())

    print("Duplicate rows:", df.duplicated().sum())

print("\n========== VALIDATION COMPLETED ==========")

# STEP 8: DATA CLEANING

print("\n========== DATA CLEANING ==========")

for name, df in tables.items():

    # Remove completely empty rows
    df.dropna(how="all", inplace=True)

    # Remove duplicate rows
    df.drop_duplicates(inplace=True)

    # Remove extra spaces from column names
    df.columns = df.columns.str.strip()

    # Remove extra spaces from text values
    for column in df.select_dtypes(include="object").columns:
        df[column] = df[column].astype(str).str.strip()

    print(name, "cleaned:", df.shape)

print("\n========== CLEANING COMPLETED ==========")

# STEP 10: CHECK JOIN COLUMNS

print("\n========== JOIN COLUMNS ==========")

print("\nBookings columns:")
print(bookings.columns.tolist())

print("\nFlights columns:")
print(flights.columns.tolist())

print("\nPassengers columns:")
print(passengers.columns.tolist())

print("\nPayments columns:")
print(payments.columns.tolist())
# STEP 11: JOIN AIRLINE TABLES

print("\n========== JOINING TABLES ==========")

# Bookings + Flights
combined = bookings.merge(
    flights,
    on="flight_id",
    how="left"
)

# Add Passenger information
combined = combined.merge(
    passengers,
    on="passenger_id",
    how="left"
)

# Add Payment information
combined = combined.merge(
    payments,
    on="booking_id",
    how="left"
)

print("Final combined shape:", combined.shape)

print("\nFinal columns:")
print(combined.columns.tolist())

print("\nFirst 5 records:")
print(combined.head())

print("\n========== JOIN COMPLETED ==========")


# STEP 12: FINAL DATA CLEANING

print("\n========== FINAL DATA CLEANING ==========")

# Remove columns starting with "Unnamed"
combined = combined.loc[
    :, ~combined.columns.str.startswith("Unnamed")
]

# Check missing values before handling them
print("\nMissing values before cleaning:")
print(combined.isnull().sum())

# Fill missing text values
text_columns = combined.select_dtypes(include="object").columns

for column in text_columns:
    combined[column] = combined[column].fillna("Unknown")

# Fill missing numeric values with median
numeric_columns = combined.select_dtypes(include="number").columns

for column in numeric_columns:
    combined[column] = combined[column].fillna(
        combined[column].median()
    )

print("\nMissing values after cleaning:")
print(combined.isnull().sum())

print("\nFinal shape:", combined.shape)

print("\n========== FINAL CLEANING COMPLETED ==========")



# STEP 13: FINAL DATA CHECK

print("\n========== FINAL DATA CHECK ==========")

print("Rows:", len(combined))
print("Columns:", len(combined.columns))

print("\nColumns:")
print(combined.columns.tolist())

print("\nSample data:")
print(combined.head(10))

print("\nDuplicate rows:", combined.duplicated().sum())

print("\n========== DATA CHECK COMPLETED ==========")



# STEP 14: FLIGHT ID VALIDATION

print("\n========== FLIGHT ID VALIDATION ==========")

# Check missing Flight IDs
missing_flight_ids = combined["flight_id"].isna().sum()

print("Missing Flight IDs:", missing_flight_ids)

# Check Flight IDs that do not exist in Flights table
valid_flight_ids = set(flights["flight_id"].dropna().astype(str))

invalid_flight_ids = combined[
    ~combined["flight_id"].astype(str).isin(valid_flight_ids)
]

print("Invalid Flight IDs:", len(invalid_flight_ids))

if len(invalid_flight_ids) > 0:
    print("\nInvalid Flight IDs found:")
    print(invalid_flight_ids["flight_id"].unique())

# Check Flight ID format
flight_id_format = combined["flight_id"].astype(str).str.match(
    r"^[A-Za-z0-9-]+$"
)

print("Invalid Flight ID format:", (~flight_id_format).sum())

print("\n========== FLIGHT ID VALIDATION COMPLETED ==========")

# STEP 16: DATE AND TIME TRANSFORMATION

print("\n========== DATE/TIME TRANSFORMATION ==========")

# Convert booking date
combined["booking_date"] = pd.to_datetime(
    combined["booking_date"],
    errors="coerce"
)

# Convert departure and arrival times
combined["departure_time"] = pd.to_datetime(
    combined["departure_time"],
    errors="coerce"
)

combined["arrival_time"] = pd.to_datetime(
    combined["arrival_time"],
    errors="coerce"
)

print("Invalid booking dates:",
      combined["booking_date"].isna().sum())

print("Invalid departure times:",
      combined["departure_time"].isna().sum())

print("Invalid arrival times:",
      combined["arrival_time"].isna().sum())

print("\nConverted date/time sample:")
print(
    combined[
        ["booking_date", "departure_time", "arrival_time"]
    ].head()
)

print("\n========== DATE/TIME TRANSFORMATION COMPLETED ==========")

# STEP 17: FLIGHT DURATION CALCULATION

print("\n========== FLIGHT DURATION ==========")

combined["calculated_duration"] = (
    combined["arrival_time"] - combined["departure_time"]
)

# Handle overnight flights
combined.loc[
    combined["calculated_duration"] < pd.Timedelta(0),
    "calculated_duration"
] += pd.Timedelta(days=1)

# Convert duration to minutes
combined["duration_minutes"] = (
    combined["calculated_duration"].dt.total_seconds() / 60
)

print("\nDuration sample:")
print(
    combined[
        ["departure_time", "arrival_time",
         "calculated_duration", "duration_minutes"]
    ].head(10)
)

print("\n========== FLIGHT DURATION COMPLETED ==========")


# STEP 18: PII MASKING

print("\n========== PII MASKING ==========")

def mask_value(value, visible=2):
    value = str(value)

    if value == "Unknown" or value == "nan":
        return "Unknown"

    if len(value) <= visible:
        return "*" * len(value)

    return value[:visible] + "*" * (len(value) - visible)


# Mask passport number
combined["passport_number"] = combined["passport_number"].apply(mask_value)

# Mask Aadhaar ID
combined["aadhaar_id"] = combined["aadhaar_id"].apply(mask_value)

# Mask phone
combined["phone"] = combined["phone"].apply(mask_value)

# Mask emergency contact phone
combined["emergency_contact_phone"] = combined[
    "emergency_contact_phone"
].apply(mask_value)

# Mask email
def mask_email(email):
    email = str(email)

    if email == "Unknown" or email == "nan":
        return "Unknown"

    if "@" not in email:
        return "****"

    name, domain = email.split("@", 1)

    return name[:2] + "****@" + domain


combined["email"] = combined["email"].apply(mask_email)

print("\nMasked PII sample:")
print(
    combined[
        [
            "passport_number",
            "aadhaar_id",
            "phone",
            "email",
            "emergency_contact_phone"
        ]
    ].head()
)

print("\n========== PII MASKING COMPLETED ==========")


# STEP 19: KPI CALCULATIONS

print("\n========== KPI CALCULATIONS ==========")

total_bookings = combined["booking_id"].nunique()

confirmed_bookings = (
    combined["status"].astype(str).str.upper() == "CONFIRMED"
).sum()

cancelled_bookings = (
    combined["status"].astype(str).str.upper() == "CANCELLED"
).sum()

pending_bookings = (
    combined["status"].astype(str).str.upper() == "PENDING"
).sum()

total_passengers = combined["passenger_id"].nunique()

total_payment = pd.to_numeric(
    combined["amount"],
    errors="coerce"
).sum()

average_payment = pd.to_numeric(
    combined["amount"],
    errors="coerce"
).mean()

print("Total bookings:", total_bookings)
print("Confirmed bookings:", confirmed_bookings)
print("Cancelled bookings:", cancelled_bookings)
print("Pending bookings:", pending_bookings)
print("Unique passengers:", total_passengers)
print("Total payment amount:", round(total_payment, 2))
print("Average payment:", round(average_payment, 2))

print("\nAirline-wise bookings:")
print(combined["airline"].value_counts())

print("\nSource-wise bookings:")
print(combined["source"].value_counts())

print("\nDestination-wise bookings:")
print(combined["destination"].value_counts())

print("\n========== KPI CALCULATIONS COMPLETED ==========")

# STEP 21: SAVE CLEANED DATA

output_file = os.path.join(
    folder,
    "cleaned_airlines.csv"
)

combined.to_csv(
    output_file,
    index=False
)

print("\nCleaned dataset saved:")
print(output_file)



# STEP 22: CREATE SQLITE DATABASE

import sqlite3

print("\n========== SQLITE DATABASE ==========")

database_file = os.path.join(
    folder,
    "airlines.db"
)

connection = sqlite3.connect(database_file)

combined.to_sql(
    "flights",
    connection,
    if_exists="replace",
    index=False
)

connection.close()

print("SQLite database created:")
print(database_file)

# STEP 23: VERIFY DATABASE

print("\n========== DATABASE VERIFICATION ==========")

connection = sqlite3.connect(database_file)

cursor = connection.cursor()

cursor.execute(
    "SELECT COUNT(*) FROM flights"
)

database_rows = cursor.fetchone()[0]

print("Rows in database:", database_rows)

cursor.execute(
    "SELECT * FROM flights LIMIT 5"
)

sample_rows = cursor.fetchall()

print("\nFirst 5 database records:")

for row in sample_rows:
    print(row)

connection.close()

print("\n========== DATABASE VERIFICATION COMPLETED ==========")


# STEP 24: FINAL PIPELINE VERIFICATION

print("\n========== FINAL PIPELINE VERIFICATION ==========")

# Check cleaned CSV
csv_exists = os.path.exists(output_file)

# Check SQLite database
db_exists = os.path.exists(database_file)

print("Cleaned CSV exists:", csv_exists)
print("SQLite database exists:", db_exists)

# Check CSV row count
if csv_exists:
    final_csv = pd.read_csv(output_file)
    print("Rows in cleaned CSV:", len(final_csv))
    print("Columns in cleaned CSV:", len(final_csv.columns))
    print("Duplicate rows in cleaned CSV:",
          final_csv.duplicated().sum())

# Check database row count
if db_exists:
    connection = sqlite3.connect(database_file)

    database_count = pd.read_sql_query(
        "SELECT COUNT(*) AS count FROM flights",
        connection
    )

    print("Rows in SQLite database:",
          database_count["count"].iloc[0])

    connection.close()

# Final result
if csv_exists and db_exists:
    print("\nPIPELINE STATUS: SUCCESS")
else:
    print("\nPIPELINE STATUS: FAILED")

print("\n========== PIPELINE COMPLETED ==========")
