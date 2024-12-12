FROM python:3.11

# Environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app/src
ENV PATH="/home/appuser/.local/bin:$PATH"

# Create and use a non-root user
RUN useradd --create-home appuser
WORKDIR /app/src
COPY --chown=appuser:appuser ./requirements.txt .

# Install global dependencies as root
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Install testing tools
RUN pip install --no-cache-dir pytest pytest-django pytest-cov

# Copy the project code into the container
COPY --chown=appuser:appuser . .

# Adjust permissions for the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose the port used by Django
EXPOSE 8000

# Command to run the Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]