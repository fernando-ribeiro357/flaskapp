docker container run -it --rm --name postman-to-openapi -v $PWD:/tmp/ groundx/postman-to-openapi p2oa convert /tmp/flaskapp.postman_collection1.json /tmp/fake_env.json -o /tmp/flaskapp_openapi.yaml
