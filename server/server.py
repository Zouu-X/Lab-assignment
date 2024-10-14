import rpyc
import re
from collections import Counter
import redis
import hashlib
import socket
import logging

# 配置日志记录
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



def getTxt(text):
    # 使用正则表达式一次性替换所有特殊字符和空白字符
    return re.sub(r'[!"$%&()*+,-./;:<=>?@[\\]^_{|}~\s]+', ' ', text.lower())

def count_words(text, word):
    # 使用Counter来计算所有单词的频率
    counts = Counter(text.split())
    return counts[word]

def read_text_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

class WordCountService(rpyc.Service):

    def on_connect(self, conn):
        self.redis_client = redis.Redis(host='redis', port=6379, db=0)

    def exposed_get_word_count(self, word, path):
        file_path = f'/app/scripts/{path}'
        # 从 Redis 获取缓存结果
        hash_key = hashlib.md5((word + file_path).encode()).hexdigest()
        count = self.redis_client.get(hash_key)
        if count is not None:
            # logging.info(f"{socket.gethostname()}:Cache hit for {word} in {path}")
            return int(count)  # 如果在缓存中找到了，直接返回结果

        # 读取和处理文件
        # logging.info(f"{socket.gethostname()}:Cache miss for {word} in {path}")
        text = read_text_from_file(file_path)
        text = getTxt(text)
        count = count_words(text, word)

        # 将结果缓存到 Redis
        self.redis_client.set(hash_key, count)
        # logging.info(f"{socket.gethostname()}:Cache set for {word} in {path}")
        return count


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    server = ThreadedServer(WordCountService, port=18812)
    server.start()
