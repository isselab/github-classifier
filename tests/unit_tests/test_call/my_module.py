#in xmi file there does not exist any call object for the call in this function
def called_func(text):
    print(text)

def caller_func():
    called_func('hello world')

caller_func()