import rpyc
import time

def main():
    # 连接到负载均衡器
    conn = rpyc.connect("rpyc-server1", 18812)
    word_to_count = "good"
    text_to_find = "spiderman.txt"

    # 开始时间戳
    start_time = time.time()

    # 发送请求等响应
    result = conn.root.get_word_count(word_to_count, text_to_find)

    # 结束时间戳
    end_time = time.time()

    exec_latency = end_time - start_time

    print(f"The word '{word_to_count}' appears {result} times in {text_to_find}")
    print(f"Execution latency: {exec_latency:.6f} seconds")
    conn.close()

if __name__ == "__main__":
    main()
