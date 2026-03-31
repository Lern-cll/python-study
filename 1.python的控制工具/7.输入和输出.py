# with open('fibo.py', 'r+', encoding='utf-8') as f:
#     read_data = f.read()
#     # print(read_data)
#
#     # f.seek(0) # 指针重塑
#     for line in f:
#         print(line, end='')
#
#     f.close()
#     print('===', f.closed)


# 为什么不能覆盖？ 因为先读，指针指向了文件的最后
with open('test.txt', 'r+', encoding='utf-8') as fr:
    read_data = fr.read()
    print(read_data)
    fr.write("\n听说你还在搞什么原创，搞来搞去好像也就这样")

#     # print(fr.readline())
#     # print(fr.readline())
#     # print(fr.readline())
    fr.seek(0) # 指针重塑
    print(fr.readlines())


