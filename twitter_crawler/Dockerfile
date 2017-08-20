# 軽量な Alpine ベースのイメージを使う
FROM python:3.6.2-alpine3.4

# Twitter ライブラリーをインストール
RUN pip install \
    twitter \
    elasticsearch

# スクリプト置き場をボリュームとして公開
VOLUME /root/scripts

# スクリプトを実行する
WORKDIR /root/scripts
CMD ["top"]
# CMD ["run_crawler.py"]
