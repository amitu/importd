
class D(object):
    class BadCall(Exception): pass
    def is_management_command(self, cmd):
        return cmd in "runserver,shell".split(",")
    
    def handle_management_command(self, cmd, *args, **kw):
        print "%s: %s %s" % (cmd, args, kw)
        
    def __call__(self, *args, **kw):
        if args:
            if self.is_management_command(args[0]):
                self.handle_management_command(*args, **kw)
                return self
            raise self.BadCall("%r %s" % (args, kw))
        else:
            from django.conf import settings
            settings.configure(**kw)
            self.settings = settings
        return self

import sys
sys.modules["amitu.d"] = D()