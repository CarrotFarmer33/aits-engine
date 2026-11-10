FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source PDFs, databases, pre-computed segments cache, and application code
COPY database.json chemistry_database.json maths_advanced_database.json maths_main_database.json ./
COPY segments_cache.json ./
COPY build_sheets.py build_chem_sheets.py build_vector_test.py server.py ./
COPY source/ ./source/

# Create generated tests directory
RUN mkdir -p /app/generated_tests

ENV PORT=8000
EXPOSE 8000

CMD ["python", "server.py"]
