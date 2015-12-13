import sys
import resource

sys.setrecursionlimit(1000000000)
resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))


"""
offset: 6027 - jt 7 reg0 6035 [7 32768 6035]
offset: 6030 - add reg0 reg1 1 [9 32768 32769 1]
offset: 6034 - ret [18]
offset: 6035 - jt reg1 6048 [7 32769 6048]
offset: 6038 - add reg0 reg0 32767 [9 32768 32768 32767]
offset: 6042 - set reg1 reg7 [1 32769 32775]
offset: 6045 - call 6027 [17 6027]
offset: 6047 - ret [18]
offset: 6048 - push reg0 [2 32768]
offset: 6050 - add reg2 reg2 32767 [9 32769 32769 32767]
offset: 6054 - call 6027 [17 6027]
offset: 6056 - set reg1 reg0 [1 32769 32768]
offset: 6059 - pop reg1 [3 32768]
offset: 6061 - add reg1 reg1 32767 [9 32768 32768 32767]
offset: 6065 - call 6027 [17 6027]
offset: 6067 - ret [18]
"""


def shenanigans(r):
    # offset: 6027 - jt 7 reg0 6035 [7 32768 6035]
    # offset: 6030 - add reg0 reg1 1 [9 32768 32769 1]
    # offset: 6034 - ret [18]
    if r[0] == 0:
        r[0] = (r[1] + 1) % 32768
        return r
    else:
        # offset: 6035 - jt reg1 6048 [7 32769 6048]
        # offset: 6038 - add reg0 reg0 32767 [9 32768 32768 32767]
        # offset: 6042 - set reg1 reg7 [1 32769 32775]
        # offset: 6045 - call 6027 [17 6027]
        # offset: 6047 - ret [18]
        if r[1] == 0:
            r[0] = (r[0] + 32767) % 32768
            r[1] = r[7]
            return shenanigans(r)
        else:
            # offset: 6048 - push reg0 [2 32768]
            # offset: 6050 - add reg1 reg1 32767 [9 32769 32769 32767]
            # offset: 6054 - call 6027 [17 6027]
            # offset: 6056 - set reg1 reg0 [1 32769 32768]
            # offset: 6059 - pop reg0 [3 32768]
            # offset: 6061 - add reg0 reg0 32767 [9 32768 32768 32767]
            # offset: 6065 - call 6027 [17 6027]
            # offset: 6067 - ret [18]
            r[1] = (r[1] + 32767) % 32768
            x = shenanigans(r)
            r[1] = x[1]
            r[0] = (r[0] + 32767) % 32768
            return shenanigans(r)


def shenanigans2(r0, r1, r7):
    global cache
    key = (r0, r1)
    try:
        return cache[key]
    except KeyError:
        if r0 == 0:
            res = (r1 + 1) % 32768
        else:
            if r1 == 0:
                r0 = (r0 + 32767) % 32768
                r1 = r7
                res = shenanigans2(r0, r1, r7)
                return res
            else:
                r1 = (r1 + 32767) % 32768
                y = shenanigans2(r0, r1, r7)
                r0 = (r0 + 32767) % 32768
                res = shenanigans2(r0, y, r7)
            print(res)
        cache[key] = res
        return res


# This versiong seems to work the best.
def shenanigans3(a, b, c):
    global cache
    k = (a, b, c)
    if k in cache:
        return cache[k]
    if a == 0:
        res = (b + 1) % 32768
    else:
        if b == 0:
            res = shenanigans3(a - 1, c, c)
        else:
            tmp = shenanigans3(a, b - 1, c)
            res = shenanigans3(a - 1, tmp, c)
    cache[k] = res
    return res


def shenanigans4(a, b, c):
    stack = []
    stack.append(a)
    stack.append(b)
    while len(stack) > 1:
        b1 = stack.pop()
        a1 = stack.pop()
        if a1 == 0:
            stack.append((b1 + 1) % 32768)
        elif b1 == 0:
            stack.append(a1 - 1)
            stack.append(c)
        else:
            stack.append(a1 - 1)
            stack.append(a1)
            stack.append(b1 - 1)
    return stack.pop()

if __name__ == "__main__":
    target = 6
    magic = 0
    for x in range(32768, 0, -1):  # Reverse iterating seems to be faster.
        cache = {}
        rslt = shenanigans3(4, 1, x)
        print("input:", x, "result:", rslt)
        if rslt == target:
            magic = x
            break
    print("magic:", magic)
