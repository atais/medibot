# Stage 1: Node build for frontend assets
FROM node:22 AS nodebuilder

WORKDIR /app

COPY package.json ./
COPY frontend ./frontend
COPY build.js ./

RUN npm install --no-audit --no-fund
RUN npm run build

# Stage 2: Python backend
FROM python:3.13-slim

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Copy built frontend assets from nodebuilder
COPY --from=nodebuilder /app/static/dist ./static/dist
COPY --from=nodebuilder /app/templates/dist.html ./templates/dist.html

# Expose the port FastAPI will run on
EXPOSE 8000

# Accept version from build args (passed from CI or local build)
ARG APP_VERSION="localbuild"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV APP_VERSION=${APP_VERSION}

# Start the FastAPI app with Uvicorn
CMD ["python", "app.py"]
