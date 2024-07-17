docker run  --cpus 1 \
            --detach \
            --memory 1073741824 \
            --name mongodb-server \
            --publish "27017:27017" \
            --restart always \
            --volume mogodb_data:/data/db \
            mongo
