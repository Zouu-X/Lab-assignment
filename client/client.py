import rpyc

def main():
    conn = rpyc.connect("rpyc-server", 18812)
    word_to_count = "spider"
    text_to_find = "spiderman.txt"
    result = conn.root.get_word_count(word_to_count, text_to_find)
    print(f"The word '{word_to_count}' appears {result} times in {text_to_find}")
    conn.close()

if __name__ == "__main__":
    main()
