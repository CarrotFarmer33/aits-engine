FROM python:3.10-slim

# Create user with UID 1000 for Hugging Face Spaces compatibility
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Install dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy source PDFs, databases, pre-computed segments cache, and application code
COPY --chown=user database.json chemistry_database.json maths_advanced_database.json maths_main_database.json ./
COPY --chown=user segments_cache.json ./
COPY --chown=user build_sheets.py build_chem_sheets.py build_vector_test.py server.py ./
COPY --chown=user source/ ./source/

# Create generated tests directory
RUN mkdir -p $HOME/app/generated_tests

ENV PORT=7860
EXPOSE 7860

CMD ["python", "server.py"]
