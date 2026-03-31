class Student:
    # 共用变量
    school = '华中复师一小'

    def __init__(self,name,age):
        self.name = name
        self.age = age

    # 表示和这个类一点关系没有完全静态
    @staticmethod
    def show():
        print('好好学习，天天向上')


    # 实例上的方法
    def get_info(self):
        print(f'name:{self.name}  age:{self.age}',self.school)

    # 类上的方法，可以访问这个类上的方法
    @classmethod
    def get_school(cls):
        return cls.school


s = Student('小明', 18)
s.show()
s.get_info()
print(s.get_school())


# mro  和 __mro__  解释这两个的作用是什么
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass
print(D.mro())


#
class Person:
    def __init__(self, name):
        self.name = name

class Child(Person):
    def __init__(self, name, age):
        super().__init__(name)
        self.age = age

p = Child("小明", 18)
print(p.name)


# 迭代器
class MyIterator:
    def __init__(self, data):
        self.data = data
        self.index = 0

    def __next__(self):
        if self.index >= len(self.data):
            raise StopIteration
        else:
            self.index += 1
            return self.data[self.index - 1]

    def __iter__(self):
        return self


it =  MyIterator('abc1234')
iter(it)
for char in it:
    print(char)

