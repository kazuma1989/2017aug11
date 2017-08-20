from threading import Timer

from elasticsearch import Elasticsearch
from twitter import Twitter, TwitterStream, OAuth

class Crawler:

    @staticmethod
    def __find_matching_trend(trend_list, tweet_text):
        for trend in trend_list:
            if trend in tweet_text:
                return trend

        # Nothing found
        return None

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

    def __push_to_index(self, tweet):
        # 取得上限超えた時にくるLimit Jsonは無視
        if "limit" in tweet:
            return tweet

        # ツイート内にキーワードが見つからないときは無視
        # 大文字・小文字の違いや、日本語表記・アルファベット表記などの揺らぎで起きることがある
        trend = self.__find_matching_trend(self.__trend_list, tweet["text"])
        if not trend:
            return

        doc = {
            "track": trend,
            "text": tweet["text"],
            "created_at": tweet["created_at"],
            # "geo": tweet["geo"],
            # "place": tweet["place"],
        }
        self.__es.index(index="testindex", doc_type="tweet", body=doc)

        return doc

    def __push_tweets_tracked_by_trend(self):
        track = ",".join(self.__trend_list)
        tweet_iter = self.__twitter_stream.statuses.filter(track=track)

        i = 0
        for tweet in tweet_iter:
            trend_list_updated = track != ",".join(self.__trend_list)
            if trend_list_updated:
                print("New trend comes")
                return

            doc = self.__push_to_index(tweet)

            i += 1
            print(i, doc)

    def __interval_refresh_trend_list(self):
        response = self.__twitter.trends.place(_id=self.__woeid)[0]["trends"]
        self.__trend_list = [trend["name"] for trend in response]

        print("Refreshed")

        self.__timer = Timer(300, self.__interval_refresh_trend_list)
        self.__timer.start()

    def run(self):
        self.__interval_refresh_trend_list()

        try:
            while True:
                self.__push_tweets_tracked_by_trend()

        except KeyboardInterrupt:
            self.__timer.cancel()
            exit()
