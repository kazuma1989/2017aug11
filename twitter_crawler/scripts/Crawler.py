from threading import Timer, get_ident

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

    def __refresh_trend_list(self):
        response = self.__twitter.trends.place(_id=self.__woeid)[0]["trends"]
        self.__trend_list = [trend["name"] for trend in response]

    def __push_tweets_tracked_by_trend(self):
        track = ",".join(self.__trend_list)
        tweet_iter = self.__twitter_stream.statuses.filter(track=track)

        i = 0
        for tweet in tweet_iter:
            if self.__current_thread_ident != get_ident():
                return

            # 取得上限超えた時にくるLimit Jsonは無視
            if "limit" in tweet:
                print(tweet)
                continue

            trend = self.__find_matching_trend(self.__trend_list, tweet["text"])
            if not trend:
                continue

            doc = {
                "track": trend,
                "text": tweet["text"],
                "created_at": tweet["created_at"],
                # "geo": tweet["geo"],
                # "place": tweet["place"],
            }

            i += 1
            print(i, doc)

            self.__es.index(index="testindex", doc_type="tweet", body=doc)

    def run(self):
        self.__current_thread_ident = get_ident()
        Timer(300, self.run).start()

        self.__refresh_trend_list()
        self.__push_tweets_tracked_by_trend()
