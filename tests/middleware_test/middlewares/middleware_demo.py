class middleware_demo(object):
    def process_view(self, request, view, *args, **kwargs):
        print("Process view called")
