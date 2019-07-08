from spiders import robotAA, robotAH, robotMA, robotMH
import scrapy
from scrapy.crawler import CrawlerProcess

rAA = robotAA.PpiSpider1()
rMA = robotMA.PpiSpider2()
rAH = robotAH.PpiSpider3()
rMH = robotMH.PpiSpider4()

process = CrawlerProcess()
process.crawl(rAA)
process.crawl(rMA)
process.crawl(rAH)
process.crawl(rMH)
process.start() # the script will block here until all crawling jobs are finished