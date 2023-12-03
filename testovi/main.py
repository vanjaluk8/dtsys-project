from fastapi import FastAPI
from pyspark_script import read_city_data
from io import BytesIO
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.get("/process_and_store")
def process_and_store():

    # Get the Pandas DataFrame
    df = read_city_data()

    # Convert DataFrame to CSV
    csv_data = df.to_csv(index=False).encode()

    # Create a BytesIO stream
    io_stream = BytesIO(csv_data)

    # Return the DataFrame as a streaming response for downloading
    return StreamingResponse(io_stream, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=city_data.csv"})

# Run the FastAPI server with uvicorn
# uvicorn main:app --reload
