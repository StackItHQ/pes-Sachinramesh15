from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from database import insert_data, create_table, fetch_data
from google_sheets import read_sheet_data, write_sheet_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_table()
    yield

app = FastAPI(lifespan=lifespan)

# ENDPOINT1: relect changes in gsheet to postgres

@app.post("/sync_postgres")
def update_postgres():
    try:
        sheet_data = read_sheet_data()
        if sheet_data:
            header = sheet_data[0]
            sheet_data = sheet_data[1:]
            print(f"Google Sheet Columns: {header}")

            insert_data(sheet_data)
            return {"message": "Data from Google Sheets inserted into PostgreSQL."}
        else:
            return {"message": "No data found in Google Sheets."}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error syncing data: {str(e)}")
    
# ENDPOINT2: reflect changes from postgres to gsheet

@app.post("/sync_gsheet")
def update_gsheet():
    try:
        db_data = fetch_data()
        if not db_data:
            return {"message": "No data found in the database."}

        header = ["lead_id", "client_name", "lead_status",
                  "assigned_sales_rep", "expected_value", "close_date"]
        formatted_data = [header] + db_data

        write_sheet_data(formatted_data)
        return {"message": "Google Sheets updated with the latest data from the database."}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating Google Sheets: {str(e)}")
    
# ENDPOINT3: fetch all entries from postgres

@app.get("/leads")
def get_leads():
    try:
        data = fetch_data()
        return {"leads": data}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching leads: {str(e)}")
