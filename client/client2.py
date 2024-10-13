import rpyc

def main():
    # 连接到负载均衡器
    conn = rpyc.connect("load-balancer", 18888)
    word_to_count = "sure"
    text_to_find = "Wonka.txt"
    result = conn.root.get_word_count(word_to_count, text_to_find)
    print(f"The word '{word_to_count}' appears {result} times in {text_to_find}")
    conn.close()

if __name__ == "__main__":
    main()
