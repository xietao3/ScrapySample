![图片来自网络](https://user-gold-cdn.xitu.io/2018/1/26/1613309f74eee5df?imageView2/1/w/1304/h/734/q/85/interlace/1)

>Python 新手入门很多时候都会写个爬虫练手，本教程使用 Scrapy 框架，帮你简单快速实现爬虫，并将数据保存至数据库。在机器学习中数据挖掘也是十分重要的，我的数据科学老师曾经说过，好算法不如好数据。

# 介绍

[Scrapy](https://scrapy.org/) ，Python 开发的一个快速、高层次的屏幕抓取和 web 抓取框架，用于抓取 web 站点并从页面中提取结构化的数据。文件结构清晰，即使是小白也能够快速上手，总之非常好用😂。

[XPath](https://baike.baidu.com/item/XPath/5574064?fr=aladdin) ,它是一种用来查找 XML 文档中节点位置的语言。 XPath 基于 XML 的树状结构，有不同类型的节点，包括元素节点，属性节点和文本节点，提供在数据结构树中找寻节点的能力。

[MySQL](https://www.mysql.com/) 是一种关系数据库管理系统，它的优势：它是免费的。作者是下载了 [MAMP for Mac](https://www.mamp.info/en/) ，内嵌``MySQL``和``Apache``。

首先通过 Scrapy 爬取到网页后， 通过 XPath 来定位指定元素，获取到你想要的数据,得到数据之后可以将数据存入数据库( MySQL )。简单了解之后就可以开始编写你的爬虫。

***重要**：下载并查看 [Demo](https://github.com/xietao3/ScrapySample) ，结合本文可以快速实现一个基本爬虫✌️。

# 准备工作

安装 Scrapy ``(系统默认安装了 Python)``:
```
$ pip install Scrapy
```
在当前目录新建工程
```
$ scrapy startproject yourproject
```
新建工程文件结构如下：
```
yourproject/
----|scrapy.cfg             # 部署配置文件
    |yourproject/           # 工程目录
    |----__init__.py
    |----items.py           # 项目数据文件
    |----pipelines.py       # 项目管道文件
    |----settings.py        # 项目设置文件
    |----spiders/           # 我们的爬虫 目录
        |----__init__.py    # 爬虫主要代码在这里    
```


简单的爬虫主要使用了``spiders``、``items``、``pipelines``这三个文件：

* spider ：爬虫的主要逻辑。
* items ：爬虫的数据模型。
* pipelines ： 爬虫获取到的数据的加工工厂，可以进行数据筛选或保存。

# 数据模型：items

![items](https://user-gold-cdn.xitu.io/2018/1/26/16132e37082a8831?w=300&h=300&f=jpeg&s=12764)

先看看我们要爬取的[网站](http://quotes.toscrape.com)，这个是 Scrapy 官方 Demo 爬取数据用的网站，我们先用这个来练手。

![quotes](https://user-gold-cdn.xitu.io/2018/1/24/16128781a79a30f4?w=1774&h=1134&f=jpeg&s=250425)

分析网页的信息我们可以看到网页主体是一个列表，列表每一行都包含可一句引用、作者名字、标签等信息。作者名右边点击（about）可以看到作者的详细信息，包括介绍、出生年月日、地点等等。根据上面的数据，我们可以先创建如下数据模型：

**items.py**

```
import scrapy

# quote 我们要爬取的主体
class QuoteItem(scrapy.Item):
    text = scrapy.Field()
    tags = scrapy.Field()
    author = scrapy.Field()

    next_page = scrapy.Field()
    pass
    
# quote 的作者信息 对应 QuoteItem.author
class AuthorItem(scrapy.Item):
    name = scrapy.Field()
    birthday = scrapy.Field()
    address = scrapy.Field()
    description = scrapy.Field()
    pass
```

所有的模型必须继承``scrapy.Item``，完成这一步我们就可以开始写爬虫的逻辑了。

```
# 完整的 QuoteItem 数据结构示例
{
    text,
    tags,
    author:{
        name,
        birthday,
        address,
        description
    }
}
```

# 爬虫：spider

![Spider](https://user-gold-cdn.xitu.io/2018/1/26/16132e022f073f10?w=200&h=200&f=jpeg&s=17148)

既然是爬虫，自然需要去爬取网页，爬虫部分的几个要点：

1. 引入你创建的数据模型
2. 首先爬虫类要继承``scrapy.Spider``。
3. 设置爬虫的名字``name``，启动爬虫时要用。
4. 将你要爬取的网址放入``start_requests()``，作为爬虫的起点。
5. 爬取的网页信息成功后，在的请求响应``parse()``中解析。


**spiders/__init__.py**

* **在顶部引入创建的数据模型。**

```
import scrapy
from ScrapySample.items import QuoteItem
from ScrapySample.items import AuthorItem
```


* **爬虫类，``name``->爬虫名字，``allowed_domains``->爬取网页的白名单。**

```
class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ["quotes.toscrape.com"]
```

* **在``start_requests()``中记录你要爬取的网址。**

    可以只放入一个网址，然后让爬虫自己爬取起始网址中下一页的链接。也可以在这里把所有需要爬的网址直接放入，比如说``page``一般是从1开始，并且有序的，写一个``for``循环可以直接输入所有页面的网址。

    本文使用的是让爬虫自己去爬取下一页网址的方式，所以只写入了一个起始网址。

```
    def start_requests(self):
        urls = [
            'http://quotes.toscrape.com/page/1/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
```

* **如下代码，爬取网页成功之后，我们要分析网页结构，找到我们需要的数据。**

    我们先来看XPath语法，``//div[@class="col-md-8"]/div[@class="quote"``：这是表示查找 class 为``"col-md-8"``的 div 节点下的一个子节点，并且子节点是一个 class 为``"quote"`` div 节点。如果在当前页面找到了这样一个节点，则返回节点信息，如果没有找到则返回``None``。

```
    def parse(self, response):
        # 通过查看器，找到列表所在的节点
        courses = response.xpath('//div[@class="col-md-8"]/div[@class="quote"]')

        for course in courses:
            # 将数据模型实例化 并从节点中找到数据填入我们的数据模型
            item = QuoteItem()
            # 轮询 course 节点下所有 class 为 "text" 的 span 节点,获取所有匹配到的节点的 text() ，由于获取到的是列表，我们默认取第一个。
            item['text'] = course.xpath('.//span[@class="text"]/text()').extract_first()
            item['author'] = course.xpath('.//small[@class="author"]/text()').extract_first()
            item['tags'] = course.xpath('.//div[@class="tags"]/a/text()').extract()

            # 请求作者详细信息
            author_url = course.xpath('.//a/@href').extract_first()
            # 如果作者介绍的链接不为空 则去请求作者的详细信息
            if author_url != '':
                request = scrapy.Request(url='http://quotes.toscrape.com'+author_url, dont_filter=True, callback=self.authorParse)
                # 将我们已经获取到的 QuoteItem 传入该请求的回调函数 authorParse()，在该函数内继续处理作者相关数据。
                request.meta['item'] = item
                yield request
        
        # 继续爬向下一页 该函数具体实现下面会分析
        next_page_request = self.requestNextPage(response)
        yield next_page_request
```

*这段注释不是很详细，如果看不懂可能需要补一下相关知识。*


* **爬取作者详细信息**

   成功获取作者详细信息 AuthorItem 后并且赋值给 QuoteItem 的属性 ``author`` ，这样一个完整的引述信息 QuoteItem 就组装完成了。
    

```
    def authorParse(self, response):
        # 先获取从 parse() 传递过来的 QuoteItem
        item = response.meta['item']
        # 通过查看器，找到作者详细信息所在节点
        sources = response.xpath('//div[@class="author-details"]')
        
        # 实例化一个作者信息的数据模型
        author_item = AuthorItem()
        # 往作者信息模型填入数据
        for source in sources:
            author_item['name'] = source.xpath('.//h3[@class="author-title"]/text()').extract_first()
            author_item['birthday'] = source.xpath('.//span[@class="author-born-date"]/text()').extract_first()
            author_item['address'] = source.xpath('.//span[@class="author-born-location"]/text()').extract_first()
            author_item['description'] = source.xpath('.//div[@class="author-description"]/text()').extract_first()
    
        # 最后将作者信息 author_item 填入 QuoteItem 
        item['author'] = author_item
        # 保存组装好的完整数据模型
        yield item
```

* **爬虫自己找到出路（下一页网页链接）**

    通过查看器我们可以找到``下一页``按钮元素，找到该节点并提取链接，爬虫即奔向下一个菜园。

```
    def requestNextPage(self, response):
        next_page = response.xpath('.//li[@class="next"]/a/@href').extract_first()
        # 判断下一个是按钮元素的链接是否存在
        if next_page is not None:
            if next_page != '':
                return scrapy.Request(url='http://quotes.toscrape.com/'+next_page, callback=self.parse)
        return None
```

爬虫的主要逻辑到这里就结束了，我们可以看到，一小段代码就可以实现一个简单的爬虫。一般主流网页都针对防爬虫做了一些处理，实操过程中也许并不会这么顺利，我们可能需要模仿浏览器的User-Agent，或者做访问延时防止请求过于频繁等等处理。

# 数据处理：pipelines

pipelines是 Scrapy 用来后续处理的管道，可以同时存在多个，并且可以自定义顺序执行，通常用来做数据处理和数据保存。我们需要在``settings.py``文件中设置需要需要执行的管道和执行顺序。

```
# 在 settings.py 加入下面的代码
ITEM_PIPELINES = {
   'ScrapySample.pipelines.ScrapySamplePipeline': 300,
}
```
在这里我只使用了一个管道``ScrapySamplePipeline``，用来将数据保存到数据库当中，后面的数字``300``是表示该管道的优先级，数字越小优先级越高。

由于我们要保存数据到数据库，所以我们需要先在本地搭建起数据库服务，我这里用的是``MySQL``，如果没有搭建的小伙伴可以下个 [MAMP](https://www.mamp.info/en/) 免费版本，安装好傻瓜式操作一键启动``Apache``、``MySQL``服务。当然，数据库和表还是要自己建的。

![MAMP](https://user-gold-cdn.xitu.io/2018/1/26/16132d56bcd4d82e?w=300&h=207&f=png&s=16004)


```
# 在 pipelines.py 中加入数据库配置信息
config = {
    'host': '127.0.0.1',
    'port': 8081,
    'user': 'root',
    'password': 'root',
    'db': 'xietao',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}
```

我们可以在``__init__()``函数里做一些初始化工作，比如说连接数据库。

然后``process_item()``函数是管道处理事件的函数，我们要在这里将数据保存入数据库，我在这个函数里写了一些插入数据库操作。

``close_spider()``函数是爬虫结束工作时候调用，我们可以在这里关闭数据库。

```
class ScrapySamplePipeline(object):

    def __init__(self):
        # 连接数据库
        self.db = sql.connect(**config)
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        # 先保存作者信息
        sql = 'INSERT INTO author (name, birthday, address, detail) VALUES (%s, %s, %s, %s)'
        self.cursor.execute(sql, (item['author']['name'], item['author']['birthday'], item['author']['address'], item['author']['description']))
        # 获取作者id
        author_id = self.cursor.lastrowid

        # 保存引述信息
        sql = 'INSERT INTO spider (text, tags, author) VALUES (%s, %s, %s)'
        self.cursor.execute(sql, (item['text'], ','.join(item['tags']), author_id))
        self.db.commit()

    # 即将结束爬虫
    def close_spider(self, spider):
        self.db.close()
        self.cursor.close()
        print('close db')
```

如果不需要保存数据库或者对数据处理的话，``pipelines``这部分是可以忽略的。这个时候在命令行切换到工程目录下，输入开始执行爬虫命令：
```
$ scrapy crawl quotes
```

部分不保存到数据库的小伙伴可以使用下方命令，将爬取的数据以 Json 格式导出到该工程目录下。

```
$ scrapy crawl quotes -o quotes.json
```

最后贴上数据库数据成功录入的截图。
![Data](https://user-gold-cdn.xitu.io/2018/1/26/161330320877c008?w=2014&h=1034&f=png&s=555547)


# 总结

这是作者最开始学习 Python 的时候写的，有一些不尽人意的地方后面会再调整，写下本文用意是巩固知识或是用于以后回顾，同时希望对同样刚开始学习 Python 的读者有所帮助。

**最后再次贴上[Demo](https://github.com/xietao3/ScrapySample) ️。**
