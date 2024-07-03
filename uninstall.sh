#!/usr/bin/env bash
docker stop milvus-standalone
docker rm milvus-standalone
docker rmi milvusdb/milvus:v2.4.5
sudo rm -rf $1/volumes
rm -rf $1/embedEtcd.yaml
