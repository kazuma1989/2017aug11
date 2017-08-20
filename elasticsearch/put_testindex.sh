#!/bin/bash
set -eux

workspace=$(dirname $0)

curl -X DELETE elastic:changeme@localhost:9200/testindex
curl -X PUT    elastic:changeme@localhost:9200/testindex -d @${workspace}/testindex.json
