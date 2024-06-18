class MyTest():
    def called_func(text):
        print(text)

    def caller_func(self):
        self.called_func('hello world')