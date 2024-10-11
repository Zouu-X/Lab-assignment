import rpyc
import redis
import hashlib


def getTxt(text):
    txt = text.lower()
    for ch in '''!"$%&()*+,-./;:<=>?@[\\]^_{|}~''\n\t ''':
        txt = txt.replace(ch, " ")
    return txt

def count_words(text, word):
    words = text.split()
    counts = {}
    for w in words:
        counts[w] = counts.get(w, 0)+1
    return counts.get(word, 0)

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
            return int(count)  # 如果在缓存中找到了，直接返回结果

        # 读取和处理文件
        text = read_text_from_file(file_path)
        text = getTxt(text)
        count = count_words(text, word)

        # 将结果缓存到 Redis
        self.redis_client.set(hash_key, count)
        return count


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    server = ThreadedServer(WordCountService, port=18812)
    server.start()
