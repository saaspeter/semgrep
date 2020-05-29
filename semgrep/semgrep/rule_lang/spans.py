# class Spanned:
#    def __init__(self, wrapped):
#        self.wrapped = wrapped
#
#    def __getattr__(self, item):
#        return getattr(self.wrapped, item)
#
#    def __getitem__(self, item):
#        return self.wrapped[item]
#
#    def __instancecheck__(self, instance):
#        return isinstance(self.wrapped, instance)
