from players.spiders.player import PlayerSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def main():
    settings = get_project_settings()
    
    process = CrawlerProcess(settings=settings)
    
    process.crawl(PlayerSpider)
    
    process.start()
    
if __name__ == "__main__":
    main()
