import re
import sys
import time
from pathlib import Path
from WeaponDataImageGeneratorBeta import WeaponInfoGenerator
from Errors import *
import requests
import warnings

warnings.filterwarnings("ignore")

if __name__ == "__main__":
    with open("./weaponHashList_2022_10_07.txt", "r") as f:
        hashList = f.read()

    hashList = re.split("\n", hashList)[:-1]

    hashListLen = len(hashList)  # 原长度
    hashListWait = hashList.copy()  # 待生成的hash列表

    WIF = WeaponInfoGenerator()

    path = "./WeaponDataImageBeta/"
    for hash in hashList:
        # 如果已经生成,则在等待列表中删除
        if Path(path+str(hash)+".png").is_file():
            if hash in hashListWait:
                hashListWait.remove(hash)
                print("{}已存在,{}/{},{:.2f}%".format(hash, len(hashListWait), hashListLen,
                                                   (1-(len(hashListWait)/hashListLen))*100))
        # 如果没有生成,则尝试生成
        else:
            lock = 1
            while lock == 1:
                try:
                    print("生成中:", end="")
                    res = WIF.generate(hash)
                    hashListWait.remove(hash)
                    if res == 0:
                        print("[{}]生成成功,{}/{},{:.2f}%".format(hash, len(hashListWait), hashListLen,
                                                               (1-(len(hashListWait)/hashListLen))*100))
                    if res == 1:
                        print("[{}]无需生成,{}/{},{:.2f}%".format(hash, len(hashListWait), hashListLen,
                                                               (1-(len(hashListWait)/hashListLen))*100))
                    lock = 0
                except DataBaseNetworkError:
                    print(1, end="")
                except requests.exceptions.ConnectTimeout:
                    print(2, end="")
                except requests.exceptions.ConnectionError:
                    print(3, end="")
