import csv

import rpyc
import time

def main():
    latencies = []
    # 连接到负载均衡器
    conn = rpyc.connect("load-balancer", 18888)
    word_to_count = "try"
    text_to_find = "spiderman.txt"

    for _ in range(50):

        # 开始时间戳
        start_time = time.time()

        # 发送请求等响应
        result = conn.root.get_word_count(word_to_count, text_to_find)

        # 结束时间戳
        end_time = time.time()

        exec_latency = end_time - start_time
        latencies.append(exec_latency)

        print(f"The word '{word_to_count}' appears {result} times in {text_to_find}")
        print(f"Execution latency: {exec_latency:.6f} seconds")
    conn.close()
    with open('/app/exec-latency/latency5.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(["Exection latency (s)"])
        for latency in latencies:
            writer.writerow([latency])
if __name__ == "__main__":
    main()
