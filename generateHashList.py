import json

jsonDataBasePos = "./jsonDataBase/zh-chs.json"

with open(jsonDataBasePos, "r", encoding='utf-8') as f:
    data = f.read()
    jsonDataBase = json.loads(data)

itemHashList = jsonDataBase["DestinyInventoryItemDefinition"].keys()

weaponHashList = []
for hash in itemHashList:
    if jsonDataBase["DestinyInventoryItemDefinition"][str(hash)]["itemType"] == 3:
        weaponHashList.append(hash)

weaponHashList.sort()

with open("weaponHashList_2022_10_07.txt", "w+") as f:
    for hash in weaponHashList:
        f.write('{}\n'.format(hash))
    print("weaponHashList done")

with open("weaponHashNameList_2022_10_07.txt", "w+") as f:
    for hash in weaponHashList:
        f.write('{}      {}\n'.format(hash, jsonDataBase["DestinyInventoryItemDefinition"][str(hash)]["displayProperties"]["name"]))
    print("weaponHashNameList done")