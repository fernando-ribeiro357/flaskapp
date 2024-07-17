docker run  --detach \
            --env ME_CONFIG_MONGODB_URL=mongodb://172.17.0.2:27017/ \
            --env ME_CONFIG_BASICAUTH=false \
            --name mongo-express \
            --publish "8081:8081" \
            --restart always \
            mongo-express
