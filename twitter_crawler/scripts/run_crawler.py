from config_oauth import OAUTH_INFO
from Crawler import Crawler

crawler = Crawler(OAUTH_INFO)
crawler.run()
