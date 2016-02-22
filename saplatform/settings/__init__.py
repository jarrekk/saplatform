import platform
try:
    from app_constant import *
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
