

# 1.基础模式
# squares = []
# for x in range(10):
#     squares.append(x**2)
# print(squares) # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]


# squares = list(map(lambda x: x**2, range(5)))
# print(squares) # [0, 1, 4, 9, 16]


# 2.带条件过滤：取偶数的平方
# evens = [x**2 for x in range(10) if x % 2 == 0]
# print(evens)  # [0, 4, 16, 36, 64]

# 3.嵌套推导：展平二维列表
# matrix = [[1, 2], [3, 4], [5, 6]]
# flat = [n for row in matrix for n in row]
# print(flat)  # [1, 2, 3, 4, 5, 6]

# 4.生成随机数列表
# import random
# randoms = [random.randint(1, 100) for _ in range(5)]
# print(randoms)  # 例如 [42, 17, 89, 3, 56]


# 5.1.2. 用列表实现队列
# from collections import deque
# deque = deque(['xiaoming', 'xiaohong', 'daqiang'])
# deque.append('张三')
# deque.append('李四')

# deque.popleft()
# deque.pop()
# print(deque)



# 5.1.3. 列表推导式
list = [(x, x**2) for x in range(8)]
print(list)

# 二维数组的推导
matrix = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
]
print(len(matrix[0]))

# 转化为列
# [[row[i] for row in matrix] for i in range(len(matrix[0]) or 4) ]

# 所有值乘2
# [[x*2 for x in col ] for col in matrix]


# 5.2. del 语句
a = [-1, 1, 66.25, 333, 333, 1234.5]
# del a[-1]
# a # [-1, 1, 66.25, 333, 333]
# del a[:]
# a # []
del a[1:]
a # [-1]


# 5.3. 元组和序列
t = 12345, 54321, 'hello!'
t

# 元组是 immutable （不可变的），一般可包含异质元素序列，通过解包（见本节下文）或索引访问
# （如果是 namedtuples，可以属性访问）。
# 列表是 mutable （可变的），列表元素一般为同质类型，可迭代访问。

##### 构造 0 个或 1 个元素的元组  () ,
empty = ()
singleton = 'hello', 


# 5.4. 集合  创建集合用花括号或 set() 函数
basket = {'apple', 'orange', 'apple', 'pear', 'orange', 'banana'}
print(basket) 
'orange' in basket

# 集合支持推导式
a = set('abracadabra')
a
{ x for x in a if x not in 'abc' }


# 5.5. 字典
tel = {'jack': 4098, 'sape': 4139}
# list(tel) # ['jack', 'guido', 'irv']


# 5.6. 循环的技巧

# https://docs.python.org/zh-cn/3/tutorial/datastructures.html#looping-techniques



