FROM adoptopenjdk:11-jre-hotspot-bionic as builder
# This stage is only used to download the AdoptOpenJDK distribution
# Stage 2: Final image with Python 3.11
FROM python:3.11-slim

# various labels
LABEL authors="vanja"
LABEL description="Dockerfile for FastAPI"
LABEL version="1.0"
LABEL hostname="fastapi-instance"

# Main workdir
WORKDIR /code

# Install Java
# Copy the JRE from the builder stage
COPY --from=builder /opt/java/openjdk /opt/java/openjdk
# Set Java environment variables
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH=$PATH:$JAVA_HOME/bin

# Main workdir
WORKDIR /code

# Copy requirements.txt
COPY ./requirements.txt /code/requirements.txt

# Install requirements
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy app main directory
COPY ./app /code/app

# run fastapi app
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]