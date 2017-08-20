from elasticsearch import Elasticsearch
from twitter import Twitter, TwitterStream, OAuth
from config_oauth import OAUTH_INFO

STREAM_INFO = {
    "timeout": 600,
    "block": False,
    # デフォルトだと90秒でストリーム維持のためのheartbeatが飛んで来るので10分に設定
    "heartbeat_timeout": 600,
}

# 日本のWOEID
WOEID_JP = 23424856

es = Elasticsearch(["http://elastic:changeme@elasticsearch:9200"])

oauth = OAuth(**OAUTH_INFO)
twitter = Twitter(auth=oauth)
twitter_stream = TwitterStream(auth=oauth, **STREAM_INFO)

trend_list = [trend["name"] for trend in twitter.trends.place(_id=WOEID_JP)[0]["trends"]]
tweet_iter = twitter_stream.statuses.filter(track=",".join(trend_list))

i = 0
for tweet in tweet_iter:
    # 取得上限超えた時にくるLimit Jsonは無視
    if "limit" in tweet:
        print(tweet)
        continue

    # どのトレンドキーワードに該当するか判定する
    for trend in trend_list:
        if trend in tweet["text"]:
            doc = {
                "track": trend,
                "text": tweet["text"],
                "created_at": tweet["created_at"],
            }

            i += 1
            print(i, doc)

            es.index(index="testindex", doc_type="tweet", body=doc)
