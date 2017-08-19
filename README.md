# Kibana のリダイレクトループ解消方法 (deprecated)

以下の issue にしたがって x-pack を取り除く：
https://github.com/elastic/kibana-docker/issues/27#issuecomment-296524205

```Dockerfile
FROM docker.elastic.co/kibana/kibana:5.5.1
RUN bin/kibana-plugin remove x-pack && \
    kibana 2>&1 | grep -m 1 "Optimization of .* complete"
```

Elasticsearch と正しく接続できれば解消するので、特別な設定をいじる必要はない。
