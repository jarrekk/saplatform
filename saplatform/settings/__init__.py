import platform
try:
    import app_constant
except:
    pass

if platform.node() == "94_54":
    from base import *
    from product import *
elif platform.node() == "JacksMacBookPro.local":
    from base import *
    from dev import *
else:
    from base import *
    from test import *
