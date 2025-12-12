# ============================
#            Builder
# ============================
FROM python:3.11-slim-bookworm AS builder

# setup environment variable  
ENV DockerHOME=/home/app/webapp

# set work directory  
RUN mkdir -p $DockerHOME  
WORKDIR $DockerHOME


# Install build dependencies
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	gcc \
	libpq-dev \
	default-libmysqlclient-dev \
	pkg-config \
	&& apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Copy requirements file and install dependencies.
COPY requirements.txt $DockerHOME 
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt



# ============================
#         Runtime Stage
# ============================
FROM python:3.11-slim-bookworm

# setup environment variable  
ENV DockerHOME=/home/app/webapp

# set work directory  
RUN mkdir -p $DockerHOME  
WORKDIR $DockerHOME

# set environment variables  
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Install runtime dependencies
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	libpq5 \
	default-libmysqlclient-dev \
	nano \
	&& apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Copy from the builder stage
COPY --from=builder /usr/local/ /usr/local/


# Copy the application code
COPY ./project $DockerHOME

RUN python manage.py collectstatic --noinput

# Set Gunicorn as the default command
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]