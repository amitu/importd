from importd import d

@d("/")
def hello(request):
    return d.HttpResponse("hello world")
    
if __name__ == "__main__":
    d.main()
