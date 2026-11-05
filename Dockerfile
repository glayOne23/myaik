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
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TZ=Asia/Jakarta

# Install runtime dependencies
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	libpq5 \
	default-libmysqlclient-dev \
	nano \
	cron \
	tzdata \
	&& ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
	&& apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Copy from the builder stage
COPY --from=builder /usr/local/ /usr/local/


# Copy the application code
COPY ./project $DockerHOME

RUN python manage.py collectstatic --noinput

# Entrypoint: daftarkan & jalankan cron (sync SIHRD tiap Sabtu 01:00) sebelum gunicorn
COPY ./docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["docker-entrypoint.sh"]

# Set Gunicorn as the default command
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]