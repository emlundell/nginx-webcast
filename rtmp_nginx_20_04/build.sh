#The following commands will download and build the custom version of rtmp nginx

# Download the rtmp module repo if not exist
if [ ! -d nginx-rtmp-module ]; then 
    git clone https://github.com/arut/nginx-rtmp-module.git
fi

# Download Nginx zip
if [ ! -f nginx.tar.gz ]; then 
    wget -O nginx.tar.gz https://nginx.org/download/nginx-1.19.0.tar.gz
fi

docker build -f dockerfile -t rtmp-nginx-20.04:latest .
