# -*- coding: utf-8 -*-


def sizeformat(size, unit='B', Standard=1000):
    division = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB', 'BB', 'NB', 'DB', 'CB', 'XB']
    loc = division.index(unit.upper())
    division = division[loc:]
    if not size:
        raise TypeError("Required argument 'size' (pos 1) not found")
    else:
        try:
            size = float(size)
        except:
            raise TypeError("Object of size must be number, not '%s'" % (type(size)))
        else:
            if (Standard != 1024) and (Standard != 1000):
                raise Exception("Convert Standard must be '1000' or '1024', not '%s'" % (Standard))
            else:
                if size < Standard:
                    return str(size) + ' ' + division[0]
                loc += 1
                for cube in range(0, len(division)):
                    if Standard ** cube >= size >= Standard ** (cube - 1):
                        if size == Standard ** cube:
                            return str(round(float(size) / Standard ** cube)) + " " + division[cube]
                        else:
                            return str(round(float(size) / Standard ** (cube - 1))) + " " + division[cube - 1]
                    else:
                        continue
                raise Exception("Out of the maximum conversion range (%s^14 %s)" % (Standard, unit))
