
# Build Nginx and RTMP with Ubuntu 20.04

# Download the rtmp module repo if not exist
if [ ! -f nginx-rtmp-module ]; then 
    git clone https://github.com/arut/nginx-rtmp-module.git
fi

# Download Nginx zip
if [ ! -f nginx.tar.gz ]; then 
    wget -O nginx.tar.gz https://nginx.org/download/nginx-1.19.0.tar.gz
fi

# Build image
docker build -t rtmp-nginx-20.04:latest -f dockerfile .
