def http_error(status_code):
    match status_code:
        case '200':
            return "Success"
        case '300' | '302':
            return 'Redirect'
        case '400':
            return 'Bad Request'
        case _:
            return "Something's wrong with the request"


# 定义坐标系的类
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
def where_is(point):
    match point:
        case Point(x=0, y=0):
            print('Origin')
        case Point(x=x, 0):
            print(f'X = {x}')
        case Point(0, y = var):
            print(f'Y = {var}')
        case Point():
            print("something wrong")
        case _:
            print("Not A Point")



