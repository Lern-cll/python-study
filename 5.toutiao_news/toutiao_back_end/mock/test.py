class MyObj:
    pass

myobj = MyObj()
myobj.id = 123
myobj.name = "小明"

print(myobj.__dict__)  # {'id': 123, 'name': '小明'}
