FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright installation
RUN python -m playwright install --with-deps chromium

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Move playwright .cache with downloaded browsers to user's home directory
RUN mkdir -p /home/appuser/.cache
RUN mv /root/.cache/ms-playwright /home/appuser/.cache/ms-playwright
RUN chown -R appuser:appuser /home/appuser/.cache

# Switch to non-root user
USER appuser

# Copy application code
COPY *.py .

# Run the application
CMD ["/app/payment-checker.py", "--config", "/app/config.yaml"]
