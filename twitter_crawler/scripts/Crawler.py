from elasticsearch import Elasticsearch
from twitter import Twitter, TwitterStream, OAuth

class Crawler:
    def __init__(self, oauth_info):
        oauth = OAuth(**oauth_info)
        self.__twitter = Twitter(auth=oauth)
        self.__twitter_stream = TwitterStream(auth=oauth, **{
            "timeout": 600,
            "block": False,
            # デフォルトだと90秒でストリーム維持のためのheartbeatが飛んで来るので10分に設定
            "heartbeat_timeout": 600,
        })

        # 日本のWOEID
        self.__woeid = 23424856

        self.__es = Elasticsearch(["http://elastic:changeme@elasticsearch:9200"])

    def __refresh_trend_list(self):
        response = self.__twitter.trends.place(_id=self.__woeid)[0]["trends"]
        self.__trend_list = [trend["name"] for trend in response]

    def __push_tweets_tracked_by(self, track):
        tweet_iter = self.__twitter_stream.statuses.filter(track=track)

        i = 0
        for tweet in tweet_iter:
            # 取得上限超えた時にくるLimit Jsonは無視
            if "limit" in tweet:
                print(tweet)
                continue

            doc = {
                "track": track,
                "text": tweet["text"],
                "created_at": tweet["created_at"],
            }

            i += 1
            print(track, i, doc)

            self.__es.index(index="testindex", doc_type="tweet", body=doc)

    def run(self):
        self.__refresh_trend_list()

        trend = self.__trend_list[0]
        self.__push_tweets_tracked_by(trend)
