# Use a lightweight Python image
FROM python:3.14-slim

# Install PDM
RUN pip install --no-cache-dir pdm

# Set the working directory inside the container
WORKDIR /app

# Copy dependency files first to leverage Docker layer caching
COPY pyproject.toml pdm.lock ./

# Install dependencies into the system environment (no virtualenv needed inside Docker)
RUN pdm install --check --prod --no-editable

# Copy the rest of your application code
COPY . .


# Start the NiceGUI application using the installed python environment
CMD ["pdm", "run", "python", "app.py"]
