FROM python:3.11


WORKDIR /app

# Install system packages and fonts
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    fonts-liberation \
    locales \
    build-essential \
    xvfb \
    xdg-utils \
    wget \
    unzip \
    libpq-dev \
    vim \
    libmagick++-dev \
    sox \
    bc \
    gsfonts \
    --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up locale
RUN locale-gen C.UTF-8 && \
    /usr/sbin/update-locale LANG=C.UTF-8
ENV LC_ALL C.UTF-8

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install MoviePy


# Modify ImageMagick policy file
RUN sed -i 's/none/read,write/g' /etc/ImageMagick-6/policy.xml && \
    sed -i 's/^.*policy domain="path".*$/<!--&-->/' /etc/ImageMagick-6/policy.xml
RUN sed -i 's/none/read,write/g' /etc/ImageMagick-6/policy.xml 
# Copy application files
COPY . .

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0

# Create output directory
RUN mkdir -p /app/output

# Expose the port the app runs on
EXPOSE 5000
ENV FLASK_APP=run.py
CMD ["flask", "run", "--host", "0.0.0.0"]