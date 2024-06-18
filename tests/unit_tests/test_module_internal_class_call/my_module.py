class MyTest():
    def called_func(text):
        print(text)

def caller_func():
    MyTest.called_func('hello world')