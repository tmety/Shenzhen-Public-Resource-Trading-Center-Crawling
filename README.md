# Shenzhen-Public-Resource-Trading-Center-Crawling
这是对深圳公共资源交易中心的中标数据进行爬取，使用request，效率比较快。

1、爬取目标数据：工程项目名称、招标人、中标人、中标价、公布时间、工期
2、因为考虑到目标网站有访问频率限制，所以在循环爬取的时候，使用了time.sleep，所以导致爬取的效率较慢
