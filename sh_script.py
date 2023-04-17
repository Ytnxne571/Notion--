import argparse
import logging
import time
import requests
import json
from notion_client import Client

parser = argparse.ArgumentParser()
parser.add_argument('cookie', help='cookie value for authentication')
parser.add_argument('notion_token', help='Notion API token')
parser.add_argument('database_id', help='Notion database ID')
args = parser.parse_args()

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# 获取当前时间
now = int(time.time())

# 向微信读书 API 发送请求，获取阅读进度
url = 'https://i.weread.qq.com/user/bookshelf?last_time={0}&page_size=20&status=1'.format(now)
headers = {
    'Cookie': args.cookie,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
response = requests.get(url, headers=headers)
data = json.loads(response.text)

# 连接 Notion API，更新数据库中的阅读进度
notion = Client(auth=args.notion_token)
db = notion.databases.retrieve(database_id=args.database_id)
for book in data['result']['book_info']:
    for page in book['reading_progress']:
        if page['is_current_reading']:
            logging.info('同步阅读进度：{0} {1} {2}'.format(book['title'], page['chapter_name'], page['page_no']))
            notion.pages.create(
                parent={
                    'database_id': db['id']
                },
                properties={
                    'Title': {
                        'title': [
                            {
                                'text': {
                                    'content': book['title']
                                }
                            }
                        ]
                    },
                    'Chapter': {
                        'rich_text': [
                            {
                                'text': {
                                    'content': page['chapter_name']
                                }
                            }
                        ]
                    },
                    'Page': {
                        'number': page['page_no']
                    }
                }
            )
