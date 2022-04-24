async def update(mode, A, B = "0"):
    f = open("info.txt","r")
    info = f.readline().split()
    if len(info) == 0:
        info = ['1', '1', '1', '0', '1', '0', '1', '1']
    f.close()
    if mode == "live":
        info[0] = A
        info[1] = B
    elif mode == "weibo":
        info[2] = A
        info[3] = B
    elif mode == "dynamic":
        info[4] = A
        info[5] = B
    elif mode == "last_dynamic":
        info[6] = A
    elif mode == "last_weibo":
        info[7] = A
    f = open("info.txt","w")
    result = ""
    for item in info:
        result += item + " "
    f.write(result)
    f.close()
    
async def new_cookie():
    f = open("cookie.txt","r")
    info = f.readline()
    return info

async def getItem(mode):
    f = open("info.txt","r")
    info = f.readline().split()
    f.close()
    if mode == "live":
        return info[0],info[1]
    elif mode == "weibo":
        return info[2],info[3]
    elif mode == "dynamic":
        return info[4],info[5]
    elif mode == "last_dynamic":
        return info[6]
    elif mode =="last_weibo":
        return info[7]

async def data_init():
    f = open("info.txt","r")
    info = f.readline().split()
    f.close()
    return info


async def words_init():
    words = []
    with open('word.txt','r') as f:
        for word in f:
            if word[-1] == '\n': 
                word = word[:-1]
            words.append(word)
    return words

async def words_add(word):
    with open('word.txt','a') as f:
        if word[-1] != '\n': word += '\n'
        f.write(word)
