import copy
import re
import sys
import time
from pathlib import Path
from WeaponDataImageGeneratorBeta import WeaponInfoGenerator
from Errors import *
import requests
import warnings
import threading
import BungieNetAPI

warnings.filterwarnings("ignore")

with open("./weaponHashListByIndex_season19.txt", "r") as f:
    hashList = f.read()

hashList = re.split("\n", hashList)[:-1]

hashListLen = len(hashList)  # 原长度
hashListWait = hashList.copy()  # 待生成的hash列表

path = "./WeaponDataImage/"

print("initialing")
time_start = time.time()
WIF_1 = WeaponInfoGenerator()
# WIF_2 = WeaponInfoGenerator()
# WIF_3 = WeaponInfoGenerator()
# WIF_4 = WeaponInfoGenerator()
# WIF_5 = WeaponInfoGenerator()
print("done,{:.3f}s".format(time.time() - time_start))


# WIF_list = [WIF_1, WIF_2, WIF_3, WIF_4, WIF_5]


def thread_wif(hash, hashListWait, hashListQueue, hashListLen, WIF):
    # 如果没有生成,则尝试生成
    lock = 1
    while lock == 1:
        try:
            # print("生成中:[{}]".format(hash), end="")
            res = WIF.generate(hash)

            if res == 0:
                print("{}生成成功,{}/{},{:.2f}%".format(hash, len(hashListWait), hashListLen,
                                                    (1 - (len(hashListWait) / hashListLen)) * 100))
            if res == 1:
                print("{}无需生成,{}/{},{:.2f}%".format(hash, len(hashListWait), hashListLen,
                                                    (1 - (len(hashListWait) / hashListLen)) * 100))
            hashListQueue.remove(hash)
            lock = 0
        except DataBaseNetworkError:
            print(1, end="")
        except requests.exceptions.ConnectTimeout:
            print(2, end="")
        except requests.exceptions.ConnectionError:
            print(3, end="")


def thread_gg(hash, hashListWait, hashListQueue, hashListLen, force_update=0):
    if Path("./spiderDataBase/lightgg/" + str(hash) + ".json").is_file() and force_update == 0:
        print("{}已经存在,{}/{},{:.2f}%".format(hash, len(hashListWait), hashListLen,
                                            (1 - (len(hashListWait) / hashListLen)) * 100))
        hashListQueue.remove(hash)
    else:
        while True:
            try:
                BungieNetAPI.spiderLightgg(hash)
                print("{}信息爬取成功,{}/{},{:.2f}%".format(hash, len(hashListWait), hashListLen,
                                                      (1 - (len(hashListWait) / hashListLen)) * 100))
                hashListQueue.remove(hash)
                return
            except DataBaseNetworkError:
                print("网络出错,重试")


if __name__ == "__main__":
    worker_num = 1
    worker_num_gg = 8
    hashListQueue = []
    mode = 'image'
    enforce_update = True

    print("mode=", mode)

    if mode == "image":
        for hash in hashList:
            # 如果已经生成,则在等待列表中删除
            if Path(path + str(hash) + ".png").is_file() and enforce_update is False:
                if hash in hashListWait:
                    hashListWait.remove(hash)
                    print("{}已存在,{}/{},{:.2f}%".format(hash, len(hashListWait), hashListLen,
                                                       (1 - (len(hashListWait) / hashListLen)) * 100))

        while True:
            if len(hashListWait) == 0:
                print("everything done")
                sys.exit()

            if len(hashListQueue) >= worker_num:
                time.sleep(0.2)
            elif len(hashListQueue) < worker_num:
                hashListQueue.append(hashListWait.pop())
                threading.Thread(target=thread_wif,
                                 args=(hashListQueue[-1], hashListWait,
                                       hashListQueue, hashListLen,
                                       WIF_1)).start()

    if mode == "gg":
        hashListWait = copy.deepcopy(hashList)
        while True:
            if len(hashListWait) == 0:
                print("everything done")
                sys.exit()

            if len(hashListQueue) >= worker_num_gg:
                time.sleep(0.1)
            elif len(hashListQueue) < worker_num_gg:
                hashListQueue.append(hashListWait.pop())
                threading.Thread(target=thread_gg,
                                 args=(hashListQueue[-1], hashListWait,
                                       hashListQueue, hashListLen,
                                       1)).start()
