import json
import sys
import time

from PIL import Image, ImageDraw, ImageFont
from BungieNetAPI import *
import Errors

class WeaponInfoGenerator:
    def __init__(self):
        # self.sc = ShortCut()  # 实例化ShortCut
        self.startTime = time.time()
        self.version = "OS-Beta"
        self.jsonDataBasePos = "./jsonDataBase/zh-chs.json"
        self.save_path = "./WeaponDataImage/"
        # self.save_path = "./"
        self.spiderPathLightgg = "./spiderDataBase/lightgg/"
        self.locale = 'zh-chs'

        self.initLocalDataBase()  # 缓存数据库
        self.initFontPath()  # 初始化字体路径

    # 初始化字体路径
    def initFontPath(self):
        # 设置各字体路径
        self.font_path_deng = "./mediaDataBase/fonts/deng.ttf"
        self.font_path_taipei = "./mediaDataBase/fonts/台北黑体粗体.ttf"
        self.font_path_sun = "./mediaDataBase/fonts/simsun.ttc"
        self.font_path_sans = "./mediaDataBase/fonts/OPENSANS-REGULAR.otf"

    # 缓存数据库
    def initLocalDataBase(self):
        with open(self.jsonDataBasePos, "r", encoding='utf-8') as f:
            data = f.read()
            self.jsonDataBase = json.loads(data)

    # 搜索本地数据库(json)
    def queryLocalDataBase(self, className, hash, locale='zh-chs'):
        # print("className={}".format(className))
        # print("hash={}".format(hash))

        hash = str(hash)
        res = self.jsonDataBase[className][hash]
        # print(res)
        return res

    # 返还相对值
    def grvl(self, xFactor, yFactor):
        if abs(xFactor) >= 1:
            xFactor = xFactor / self.resol
        if abs(yFactor) >= 1:
            yFactor = yFactor / self.resol
        return [int(self.resol * xFactor), int(self.resol * yFactor)]
    def grv(self, Factor):
        if abs(Factor) >= 1:
            Factor = Factor / self.resol
        return int(self.resol * Factor)
    def grv_pixel(self, Factor):
        Factor = Factor / self.resol
        return int(self.resol * Factor)

    # 生成图片
    def generate(self, weapon_hash):
        self.weapon_hash = weapon_hash
        # 设置语言为简体中文
        locale = self.locale

        mode = 'net'
        enforce_net = True
        # 收集lightgg数据
        if mode == 'net':
            if Path("./spiderDataBase/lightgg/" + str(self.weapon_hash) + ".json").is_file() and enforce_net is False:
                with open("./spiderDataBase/lightgg/" + str(self.weapon_hash) + ".json", "r") as f:
                    lightgg_json = json.loads(f.read())
                lightggdata_time = os.path.getmtime("./spiderDataBase/lightgg/" + str(self.weapon_hash) + ".json")
            else:
                lightgg_json = spiderLightgg(self.weapon_hash)
                lightggdata_time = time.time()
        elif mode == 'default':
            with open("./spiderDataBase/default.json", "r") as f:
                lightgg_json = json.loads(f.read())
                lightggdata_time = os.path.getmtime("./spiderDataBase/default.json")

        # 收集基础数据
        if True:
            # 获取武器物品信息
            weapon_json = self.queryLocalDataBase("DestinyInventoryItemDefinition", self.weapon_hash, locale=locale)
            # 只生成传说和异域武器
            if "summaryItemHash" not in weapon_json:
                return 1
            if weapon_json["summaryItemHash"] not in [75112946, 3520001075, 2673424576]:
                return 1

            # 获取武器伤害类型信息
            weapon_damageType_json = self.queryLocalDataBase("DestinyDamageTypeDefinition", weapon_json["defaultDamageTypeHash"], locale=locale)
            # 获取武器收集品信息
            if "collectibleHash" in weapon_json:
                weapon_collectible_json = self.queryLocalDataBase("DestinyCollectibleDefinition", weapon_json["collectibleHash"], locale=locale)
            # 获取武器框架信息
            weapon_archeType_json = self.queryLocalDataBase("DestinyInventoryItemDefinition", weapon_json["sockets"]["socketEntries"][0]["singleInitialItemHash"], locale=locale)
            # 获取武器框架的沙盒信息
            weapon_archeType_sandBox_json = self.queryLocalDataBase("DestinySandboxPerkDefinition", weapon_archeType_json["perks"][0]["perkHash"], locale=locale)
            # 获取武器perkSet
            weapon_perkSet_jsonList = []
            for index in [1, 2, 3, 4, 8]:
                try:
                    if "randomizedPlugSetHash" in weapon_json["sockets"]["socketEntries"][index]:
                        weapon_perkSet_jsonList.append(self.queryLocalDataBase("DestinyPlugSetDefinition", weapon_json["sockets"]["socketEntries"][index]["randomizedPlugSetHash"], locale=locale))
                    elif "reusablePlugSetHash" in weapon_json["sockets"]["socketEntries"][index]:
                        weapon_perkSet_jsonList.append(self.queryLocalDataBase("DestinyPlugSetDefinition", weapon_json["sockets"]["socketEntries"][index]["reusablePlugSetHash"], locale=locale))
                except IndexError:
                    pass

            # 把需要加载的图片压入字典
            image_url_dict = {
                "weapon_screenShot": weapon_json["screenshot"],
                "weapon_icon": weapon_json["displayProperties"]["icon"],
                "weapon_damageType_icon": weapon_damageType_json["displayProperties"]["icon"],
                "weapon_archeType_icon": weapon_archeType_json["displayProperties"]["icon"]
            }
            # 处理有武器不存在水印的问题
            if "iconWatermark" in weapon_json:
                image_url_dict["weapon_icon_waterMark"] = weapon_json["iconWatermark"]

            # 将字典的值转换成列表,遍历查询本地是否存在,不存在则会自动下载
            image_url_values = image_url_dict.values()
            for url in image_url_values:
                loadPicture(url)

            # 把需要的文本信息压入字典
            weapon_info_dict = {
                "weapon_name": weapon_json["displayProperties"]["name"],
                "weapon_type": weapon_json["itemTypeDisplayName"],
                "weapon_ammoType": weapon_json["equippingBlock"]["ammoType"],
                "weapon_flavorText": weapon_json["flavorText"],
                "weapon_archeType_name": weapon_archeType_json["displayProperties"]["name"]
            }
            try:
                weapon_info_dict["weapon_archeType_description"] = weapon_archeType_sandBox_json["displayProperties"]["description"]
            except Exception:
                weapon_info_dict["weapon_archeType_description"] = weapon_archeType_json["displayProperties"]["description"]
            try:
                weapon_info_dict["weapon_source"] = weapon_collectible_json["sourceString"]
            except Exception:
                weapon_info_dict["weapon_source"] = ""

        # 收集武器参数信息
        if True:
            weapon_stats_list = weapon_json["stats"]["stats"]
            weapon_stats_value_dict = {}
            # hash2name对照表
            weapon_stat_hash2name_dict = {
                "155624089": "stability",  # 稳定性
                "943549884": "handling",  # 操控性
                "1240592695": "range",  # 射程
                "1345609583": "aa",  # 空中效率
                "1931675084": "inventorySize",  # 物品栏空间
                "2714457168": "ae",  # 空中效率
                "2715839340": "recoilDirection",  # 后座方向
                "3555269338": "zoom",  # 变焦
                "3871231066": "magazine",  # 弹匣
                "4043523819": "impact",  # 伤害
                "4188031367": "reloadSpeed",  # 换弹速度
                "4284893193": "rpm",  # 每分钟发射数
                "447667954": "drawTime",  # 弓的蓄力时间
                "1591432999": "accuracy",  # 弓的精度
                "2961396640": "chargeTime",  # 融合和线性融合的充能时间(弓也有,但是弓的值小于100)
                "3614673599": "blastRadius",  # 榴弹和火箭筒的爆炸范围
                "2523465841": "velocity"  # 榴弹和火箭筒的弹头速度
            }
            # 通过hash2name生成name2hash对照表
            weapon_stat_name2hash_dict = {}
            for i in range(len(weapon_stat_hash2name_dict)):
                weapon_stat_name2hash_dict[list(weapon_stat_hash2name_dict.values())[i]] = \
                list(weapon_stat_hash2name_dict.keys())[i]
            # 向weapon_stats_value_dict写入武器参数
            for stat in weapon_stats_list:
                stat_hash = str(weapon_stats_list[stat]["statHash"])
                if stat_hash in weapon_stat_hash2name_dict:
                    exec("weapon_stats_value_dict['"+weapon_stat_hash2name_dict[stat]+"'] = weapon_stats_list[stat_hash]['value']")

        # 开始绘制,做一些准备工作
        if True:
            # 设置画布宽高
            canvas_width = 1000
            canvas_height = 1500
            self.resol = canvas_width

            # 设置一些其他参数
            margin = self.grv(20)  # 边框
            defaultFont = ImageFont.truetype(self.font_path_sun, 13)
            numberFont = ImageFont.truetype(self.font_path_sans, 13)

            # 新建画布
            canvas = Image.new("RGB", (canvas_width, canvas_height), "#000000")
            draw = ImageDraw.Draw(canvas)

            # 定义颜色
            gray = (45, 45, 45)

        # 绘制背景
        if True:
            # 读取武器截图作为背景图片
            weapon_screenShot = Image.open("./mediaDataBase" + image_url_dict["weapon_screenShot"])  # 读取图片
            weapon_screenShot_width, weapon_background_height = weapon_screenShot.size  # 读取图片宽高
            weapon_screenShot_width_new = int(canvas_width)  # 新宽=画布宽
            weapon_screenShot_height_new = int((weapon_background_height/weapon_screenShot_width) * weapon_screenShot_width_new)  # 新高=新宽*高宽比
            weapon_screenShot = weapon_screenShot.resize((weapon_screenShot_width_new, weapon_screenShot_height_new))  # 缩放
            canvas.paste(weapon_screenShot)  # 把武器截图贴到画布上

            # 为武器截图添加渐变效果

            # 截图下面的渐变效果
            weapon_screenShot_fade = Image.open("./mediaDataBase/custom/fade.png")  # 读取图片
            weapon_screenShot_fade_width_new = int(canvas_width)  # 新宽=画布宽
            weapon_screenShot_fade_height_new = int(canvas_width * 0.2)  # 新高=画布宽*系数
            weapon_screenShot_fade = weapon_screenShot_fade.resize((weapon_screenShot_fade_width_new, weapon_screenShot_fade_height_new))  # 缩放
            weapon_screenShot_fade_mask = weapon_screenShot_fade.convert("RGBA")  # 创建蒙版
            weapon_screenShot_fade_position = (0, int(canvas_width * 0.365))
            canvas.paste(weapon_screenShot_fade, weapon_screenShot_fade_position, mask=weapon_screenShot_fade_mask)
            #截图上面的渐变效果
            weapon_screenShot_fadeUpper = Image.open("./mediaDataBase/custom/fade.png")  # 读取图片
            weapon_screenShot_fadeUpper = weapon_screenShot_fadeUpper.transpose(Image.Transpose.FLIP_TOP_BOTTOM)  # 上下翻转
            weapon_screenShot_fadeUpper_width_new = int(canvas_width)  # 新宽=画布宽
            weapon_screenShot_fadeUpper_height_new = int(canvas_width * 0.1)  # 新高=画布宽*系数
            weapon_screenShot_fadeUpper = weapon_screenShot_fadeUpper.resize((weapon_screenShot_fadeUpper_width_new, weapon_screenShot_fadeUpper_height_new))  # 缩放
            weapon_screenShot_fadeUpper_mask = weapon_screenShot_fadeUpper.convert("RGBA")  # 创建蒙版
            weapon_screenShot_fadeUpper_position = (0, self.grv(0))
            canvas.paste(weapon_screenShot_fadeUpper, weapon_screenShot_fadeUpper_position, mask=weapon_screenShot_fadeUpper_mask)
            # 截图左边的渐变效果
            weapon_screenShot_fadeLeft = Image.open("./mediaDataBase/custom/fade.png")
            weapon_screenShot_fadeLeft = weapon_screenShot_fadeLeft.resize((self.grv(0.6), self.grv(0.2)))
            weapon_screenShot_fadeLeft = weapon_screenShot_fadeLeft.transpose(Image.Transpose.ROTATE_270)
            canvas.paste(weapon_screenShot_fadeLeft, (0, 0), mask=weapon_screenShot_fadeLeft.convert("RGBA"))
            # 截图右边的渐变效果
            weapon_screenShot_fadeLeft = Image.open("./mediaDataBase/custom/fade.png")
            weapon_screenShot_fadeLeft = weapon_screenShot_fadeLeft.resize((self.grv(0.6), self.grv(0.20)))
            weapon_screenShot_fadeLeft = weapon_screenShot_fadeLeft.transpose(Image.Transpose.ROTATE_90)
            canvas.paste(weapon_screenShot_fadeLeft, (self.grv(0.8), 0), mask=weapon_screenShot_fadeLeft.convert("RGBA"))

        # 绘制武器图标
        if True:
            # 添加武器图标
            weapon_icon_size_factor = 0.111  # 大小系数
            weapon_icon = Image.open("./mediaDataBase" + image_url_dict["weapon_icon"])  # 读取图片
            weapon_icon_width, weapon_icon_height = weapon_icon.size  # 读取图片宽高
            weapon_icon_width_new = int(canvas_width * weapon_icon_size_factor)  # 新宽=画布宽*系数
            weapon_icon_height_new = int(weapon_icon_width_new * (weapon_icon_height / weapon_icon_width))  # 新高=新宽*高宽比
            weapon_icon = weapon_icon.resize((weapon_icon_width_new, weapon_icon_height_new))  # 缩放
            weapon_icon_position = (margin, margin)  # 武器图标坐标
            canvas.paste(weapon_icon, weapon_icon_position)  # 把武器图标贴到画布上
            # 添加武器水印(如果有)
            if "weapon_icon_waterMark" in image_url_dict:
                weapon_icon_waterMark = Image.open("./mediaDataBase" + image_url_dict["weapon_icon_waterMark"])  # 读取图片
                weapon_icon_waterMark = weapon_icon_waterMark.resize(weapon_icon.size)  # 将水印和武器图标大小同步
                weapon_icon_waterMark_mask = weapon_icon_waterMark.convert("RGBA")  # 创建蒙版
                canvas.paste(weapon_icon_waterMark, weapon_icon_position, mask=weapon_icon_waterMark_mask)  # 将水印贴到武器图标的位置
            # 给武器图标加上边框
            draw.rectangle((weapon_icon_position[0], weapon_icon_position[1],
                            weapon_icon_position[0]+weapon_icon.size[0], weapon_icon_position[1]+weapon_icon.size[1]),
                           outline="#ffffff", width=1)

        # 编辑武器图标右侧的信息
        if True:
            # 武器名称
            font = ImageFont.truetype(self.font_path_taipei, size=int(canvas_width * 0.03))
            draw.text((int(canvas_width * 0.148), int(canvas_width * 0.048)), weapon_info_dict["weapon_name"], font=font, anchor="ls")
            # 武器伤害类型图标
            weapon_damageType_icon = Image.open("./mediaDataBase" + image_url_dict["weapon_damageType_icon"])  # 读取图片
            weapon_damageType_icon = weapon_damageType_icon.resize(self.grvl(18, 18), resample=Image.Resampling.LANCZOS)  # 更改大小
            canvas.paste(weapon_damageType_icon, self.grvl(149, 61), mask=weapon_damageType_icon.convert("RGBA"))
            # 武器弹药图标
            if weapon_info_dict["weapon_ammoType"] == 1:
                weapon_ammoType_icon = Image.open("./mediaDataBase/custom/ammoType/primary.png")
            elif weapon_info_dict["weapon_ammoType"] == 2:
                weapon_ammoType_icon = Image.open("./mediaDataBase/custom/ammoType/special.png")
            elif weapon_info_dict["weapon_ammoType"] == 3:
                weapon_ammoType_icon = Image.open("./mediaDataBase/custom/ammoType/heavy.png")
            weapon_ammoType_icon = weapon_ammoType_icon.resize(self.grvl(22, 16), resample=Image.Resampling.LANCZOS)  # 更改大小
            canvas.paste(weapon_ammoType_icon, self.grvl(171, 62), mask=weapon_ammoType_icon.convert("RGBA"))  # 粘贴
            # 武器类别
            draw.text(self.grvl(197, 75), weapon_info_dict["weapon_type"], font=defaultFont, anchor="ls")
            # 武器来源
            draw.text(self.grvl(149, 100), weapon_info_dict["weapon_source"], font=defaultFont, anchor="ls")
            # 特色文字
            draw.text(self.grvl(149, 125), weapon_info_dict["weapon_flavorText"], font=defaultFont, anchor="ls")

        # 绘制武器参数
        if True:
            gap = self.grv(19)
            cursor = self.grvl(100, 161)
            stat_print_list = ["chargeTime",
                               "drawTime",
                               "rpm",

                               "impact",
                               "range",
                               "blastRadius",
                               "velocity",

                               "stability",
                               "handling",
                               "reloadSpeed",
                               "aa",
                               "ae",
                               "zoom",
                               "recoilDirection",
                               "magazine"]
            # 遍历列表按顺序打印
            for stat_name in stat_print_list:
                # 如果武器有对应的参数则尝试打印
                if stat_name in weapon_stats_value_dict:
                    # 忽视值小于100的充能时间
                    if stat_name == "chargeTime" and weapon_stats_value_dict["chargeTime"] <= 100:
                        continue
                    statHash = weapon_stat_name2hash_dict[stat_name]
                    # 打印参数名称
                    statNamePrint = self.queryLocalDataBase("DestinyStatDefinition", statHash, locale=locale)["displayProperties"]["name"]
                    draw.text(cursor, statNamePrint, font=defaultFont, anchor="rs",
                              stroke_width=1, stroke_fill="#000000")
                    # 打印参数数值
                    statValuePrint = str(weapon_stats_value_dict[stat_name])
                    draw.text((cursor[0]+self.grv(30), cursor[1]), statValuePrint,
                              font=numberFont, anchor="rs",
                              stroke_width=1, stroke_fill="#000000")
                    # 绘制数值条
                    barLength = self.grv(225)
                    barHeight = self.grv(14)
                    if stat_name not in ["recoilDirection", "rpm", "drawTime", "chargeTime", "magazine"]:
                        # 底色
                        draw.rectangle([cursor[0]+self.grv(40), cursor[1]-self.grv(12),
                                       cursor[0]+self.grv(40)+barLength, cursor[1]-self.grv(12)+barHeight],
                                       fill=gray)
                        # 上色
                        draw.rectangle([cursor[0] + self.grv(40),
                                        cursor[1] - self.grv(12),
                                        cursor[0] + self.grv(40) + int(barLength * int(statValuePrint) / 100),
                                        cursor[1] - self.grv(12) + barHeight],
                                       fill="#ffffff")
                    # 绘制后座方向的饼图
                    if stat_name == "recoilDirection":
                        # 底色
                        draw.pieslice([cursor[0]+self.grv(40), cursor[1]-self.grv(12),
                                       cursor[0]+self.grv(40)+self.grv(27), cursor[1]-self.grv(12)+2*barHeight],
                                      start=180, end=360, fill=gray)
                        # 上色
                        value = 100 - int(statValuePrint)
                        draw.pieslice([cursor[0] + self.grv(40), cursor[1] - self.grv(12),
                                       cursor[0] + self.grv(40) + self.grv(27),
                                       cursor[1] - self.grv(12) + 2 * barHeight],
                                      start=270-value-4, end=270+value+4, fill="#ffffff")

                    # 更新指针位置
                    cursor[1] += gap

        # 绘制武器框架
        if True:
            cursor = self.grvl(20, 360)
            # 绘制底色
            draw.rectangle([cursor[0],
                            cursor[1],
                            self.grv(365),
                            cursor[1] + self.grv(52)],
                           fill=gray)
            # 绘制框架图标
            weapon_archeType_icon = Image.open("./mediaDataBase" + image_url_dict["weapon_archeType_icon"])
            weapon_archeType_icon = weapon_archeType_icon.resize(self.grvl(38, 38), resample=Image.Resampling.LANCZOS)
            canvas.paste(weapon_archeType_icon, (cursor[0]+self.grv(12), cursor[1]+self.grv(7)), mask=weapon_archeType_icon.convert("RGBA"))
            # 框架名称
            draw.text((cursor[0]+self.grv(55), cursor[1]+self.grv(21)),
                      weapon_info_dict["weapon_archeType_name"],
                      font=defaultFont, anchor="ls")
            # 框架注释
            draw.text((cursor[0] + self.grv(55), cursor[1] + self.grv(40)),
                      weapon_info_dict["weapon_archeType_description"],
                      font=defaultFont, anchor="ls")

        # 绘制武器perk
        if True:
            cursor = [cursor[0]+self.grv(16), cursor[1]+self.grv(70)]
            cursor_perk = cursor
            # 如果没有流行perk数据
            if lightgg_json["popularPerk"] == [[], [], [], [], []]:
                perkSize = 28  # perk图标大小
                perkGapX = 50  # perk的X间距
                perkGapY = 44  # perk的Y间距
                perkCircleSize = 36  # perk外圈大小
                perkCircleWidth = 2  # perk圈宽度
                lineOffset = 0  # 分割线偏移值
            # 如果有流行perk数据
            else:
                perkSize = 28  # perk图标大小
                perkGapX = 70  # perk的X间距
                perkGapY = 44  # perk的Y间距
                perkCircleSize = 36  # perk外圈大小
                perkCircleWidth = 2  # perk圈宽度
                lineOffset = 6  # 分割线偏移值

            maxPerkNum = 0  # 最多的同槽位perk数量

            # 删除列表里重复的perk
            for row_num in range(len(weapon_perkSet_jsonList)):
                return_list = []
                for perk in weapon_perkSet_jsonList[row_num]["reusablePlugItems"]:
                    if perk not in return_list:
                        return_list.append(perk)
                weapon_perkSet_jsonList[row_num]["reusablePlugItems"] = return_list
            # 删除列表里已弃用但又启用的perk
            for row_num in range(len(weapon_perkSet_jsonList)):
                for perk in weapon_perkSet_jsonList[row_num]["reusablePlugItems"]:
                    if not perk["currentlyCanRoll"]:
                        perk_test = perk.copy()
                        perk_test["currentlyCanRoll"] = True
                        if weapon_perkSet_jsonList[row_num]["reusablePlugItems"].count(perk_test):
                            weapon_perkSet_jsonList[row_num]["reusablePlugItems"].remove(perk)

            # 遍历perk槽位,绘制perk和perk圈
            for row_num in range(len(weapon_perkSet_jsonList)):
                if len(weapon_perkSet_jsonList[row_num]["reusablePlugItems"]) > maxPerkNum:
                    maxPerkNum = len(weapon_perkSet_jsonList[row_num]["reusablePlugItems"])

                # 遍历该槽位perk
                for index in range(len(weapon_perkSet_jsonList[row_num]["reusablePlugItems"])):
                    perk_hash = weapon_perkSet_jsonList[row_num]["reusablePlugItems"][index]["plugItemHash"]  # perk hash
                    perk_json = self.queryLocalDataBase("DestinyInventoryItemDefinition", perk_hash, locale=locale)  # perk json
                    perk_name = perk_json["displayProperties"]["name"]  # perk 名字
                    perk_icon_url = perk_json["displayProperties"]["icon"]  # perk图标url
                    loadPicture(perk_icon_url)  # 加载perk图标

                    icon_pos = (cursor[0]+int(self.grv(perkGapX*row_num)), cursor[1]+int(self.grv(perkGapY*index)))  # perk图标位置
                    perk_icon = Image.open("./mediaDataBase" + perk_icon_url)  # 读取perk图标
                    perk_icon = perk_icon.resize(self.grvl(perkSize, perkSize), resample=Image.Resampling.LANCZOS)  # 缩放
                    canvas.paste(perk_icon, icon_pos, mask=perk_icon.convert("RGBA"))  # 绘制perk图标

                    # 外圈颜色
                    perkCircleColor = "#ffffff"
                    # perk当前是否启用
                    perkCurrentlyCanRoll = weapon_perkSet_jsonList[row_num]["reusablePlugItems"][index]["currentlyCanRoll"]
                    # 如果perk不可抽取则外圈变红
                    if not perkCurrentlyCanRoll:
                        perkCircleColor = "#ff0000"

                    # perk锻造等级
                    requiredLevel = -1
                    if "craftingRequirements" in weapon_perkSet_jsonList[row_num]["reusablePlugItems"][index]:
                        if "requiredLevel" in weapon_perkSet_jsonList[row_num]["reusablePlugItems"][index]["craftingRequirements"]:
                            requiredLevel = weapon_perkSet_jsonList[row_num]["reusablePlugItems"][index]["craftingRequirements"]["requiredLevel"]

                    # perk是否为强化perk
                    if perk_json["inventory"]["tierType"] == 3:
                        perkCircleColor = "#ffd700"

                    # 绘制perk的外圈
                    draw.arc([icon_pos[0]+self.grv(perkSize/2-perkCircleSize/2-1),
                              icon_pos[1]+self.grv(perkSize/2-perkCircleSize/2),
                              icon_pos[0]+self.grv(perkSize/2+perkCircleSize/2-1),
                              icon_pos[1]+self.grv(perkSize/2+perkCircleSize/2)],
                             start=0, end=360, width=perkCircleWidth, fill=perkCircleColor)

                    # 绘制锻造perk所需的等级
                    if requiredLevel != -1:
                        draw.text([icon_pos[0]+self.grv(perkSize-1),
                                   icon_pos[1]+self.grv(perkSize-4)],
                                  str(requiredLevel),
                                  font=ImageFont.truetype(self.font_path_sans, 8))

                    # 画perk流行数据标识(如果有)
                    if lightgg_json["popularPerk"]:
                        for index in range(len(lightgg_json["popularPerk"][row_num])):
                            perk = lightgg_json["popularPerk"][row_num][index]
                            # 第一个为最流行的perk,获取其大众程度
                            if index == 0:
                                perk_popularity_max = float(perk["perkPopularity"][:-1])
                            # 按哈希值匹配
                            if perk["perkHash"] == str(perk_hash):
                                perk_popularity = float(perk["perkPopularity"][:-1])
                                # perk颜色
                                perk_popularity_color = (int((1 - perk_popularity / perk_popularity_max) * 255),
                                                         int(perk_popularity / perk_popularity_max * 255),
                                                         0)
                                # perk条位置
                                perkPopularityBar_pos = self.grvl(icon_pos[0] + perkCircleSize + 2, icon_pos[1] - 4)
                                # 画显示条
                                draw.rectangle([perkPopularityBar_pos[0],
                                                perkPopularityBar_pos[1] + self.grv_pixel(perkCircleSize * (1 - perk_popularity / perk_popularity_max)),
                                                perkPopularityBar_pos[0] + self.grv(10),
                                                perkPopularityBar_pos[1] + self.grv(perkCircleSize)],
                                               fill=perk_popularity_color)
                                # 画外框
                                draw.rectangle([perkPopularityBar_pos[0],
                                                perkPopularityBar_pos[1],
                                                perkPopularityBar_pos[0] + self.grv(10),
                                                perkPopularityBar_pos[1] + self.grv(perkCircleSize)],
                                               outline=perk_popularity_color)
                                # 写字
                                if perk_popularity != 100:
                                    draw.text(self.grvl(perkPopularityBar_pos[0] + 5,
                                                        perkPopularityBar_pos[1] + perkCircleSize/2),
                                              "{:.0f}".format(perk_popularity),
                                              font=ImageFont.truetype(self.font_path_deng, size=10),
                                              anchor="mm",
                                              stroke_fill="#000000", stroke_width=1)


            # 画不同槽位perk间的分割线
            for row_num in range(len(weapon_perkSet_jsonList) - 1):
                linePos = [cursor[0] + self.grv(perkGapX/2 + perkSize/2 + perkGapX * row_num + lineOffset),
                           cursor[1] - perkSize/4,
                           cursor[0] + self.grv(perkGapX/2 + perkSize/2 + perkGapX * row_num + lineOffset),
                           cursor[1] - perkSize/4 + self.grv(maxPerkNum*perkGapY)]
                draw.line(linePos, fill=gray)

        # 绘制稀有度
        if True:
            weapon_communityRarity = float(lightgg_json["communityRarity"][:-1])

            rarityPie_size = 100
            rarityPie_position_x = 880
            rarityPie_position_y = 20
            rarityPie_text_size = 10

            if lightgg_json["popularPerkSampleNum"] != "<":

                # 画底色
                draw.arc([self.grv(rarityPie_position_x),
                          self.grv(rarityPie_position_y),
                          self.grv(rarityPie_position_x + rarityPie_size),
                          self.grv(rarityPie_position_y + rarityPie_size)],
                         start=0, end=360,
                         width=self.grv(0.01), fill=gray)
                # 画拥有该枪的玩家数的弧线
                draw.arc([self.grv(rarityPie_position_x),
                          self.grv(rarityPie_position_y),
                          self.grv(rarityPie_position_x + rarityPie_size),
                          self.grv(rarityPie_position_y + rarityPie_size)],
                         start=-90, end=360*weapon_communityRarity*0.01 - 90,
                         width=self.grv(0.01))
                # 写拥有该枪的玩家数的百分比
                draw.text([self.grv(rarityPie_position_x + rarityPie_size / 2),
                           self.grv(rarityPie_position_y + rarityPie_size / 2 - 6)],
                          "{:.0f}%玩家已拥有".format(weapon_communityRarity),
                          font=ImageFont.truetype(self.font_path_taipei, size=rarityPie_text_size),
                          anchor="mm")
                # 写该武器的总个数(如果有)
                if lightgg_json["popularPerkSampleNum"] != 0 and str(lightgg_json["popularMWSampleNum_fullPercent"]) != "0"\
                        and "%" in str(lightgg_json["popularMWSampleNum_fullPercent"]):
                    weapon_popularPerkSampleNum = lightgg_json["popularPerkSampleNum"]
                    weapon_popularMWSampleNum = lightgg_json["popularMWSampleNum"]
                    weapon_popularModSampleNum = lightgg_json["popularModSampleNum"]
                    weapon_popularMWSampleNum_fullPercent = float(lightgg_json["popularMWSampleNum_fullPercent"][:-1])
                    if lightgg_json["popularMWSampleNum_fullNum"] == "<1.0K":
                        lightgg_json["popularMWSampleNum_fullNum"] = "1.0K+"
                    weapon_popularMWSampleNum_fullNum = float(lightgg_json["popularMWSampleNum_fullNum"][:-2])
                    gun_num = weapon_popularMWSampleNum_fullNum / (weapon_popularMWSampleNum_fullPercent / 100)

                    draw.text([self.grv(rarityPie_position_x + rarityPie_size / 2),
                               self.grv(rarityPie_position_y + rarityPie_size / 2 - 18)],
                              "(共{:.1f}K+件)".format(gun_num),
                              font=ImageFont.truetype(self.font_path_taipei, size=rarityPie_text_size),
                              anchor="mm")
                # 画完全大师的弧线(如果有)
                if lightgg_json["popularMWSampleNum_fullPercent"] != 0 and lightgg_json["popularMWSampleNum"] != "<":
                    weapon_popularMWSampleNum_fullPercent = float(lightgg_json["popularMWSampleNum_fullPercent"][:-1])
                    draw.arc([self.grv(rarityPie_position_x),
                              self.grv(rarityPie_position_y),
                              self.grv(rarityPie_position_x + rarityPie_size),
                              self.grv(rarityPie_position_y + rarityPie_size)],
                             start=-90, end=360*weapon_communityRarity*0.01*weapon_popularMWSampleNum_fullPercent*0.01- 90,
                             width=self.grv(0.01), fill="#ff7d00")
                # 写完全大师的百分比(如果有)
                    draw.text([self.grv(rarityPie_position_x + rarityPie_size / 2),
                               self.grv(rarityPie_position_y + rarityPie_size / 2 + 6)],
                              "{:.0f}%已完全大师".format(weapon_popularMWSampleNum_fullPercent),
                              font=ImageFont.truetype(self.font_path_taipei, size=rarityPie_text_size),
                              anchor="mm", fill="#ff7d00")
                # 写完全大师的个数(如果有)
                    weapon_popularMWSampleNum_fullNum = lightgg_json["popularMWSampleNum_fullNum"]
                    draw.text([self.grv(rarityPie_position_x + rarityPie_size / 2),
                               self.grv(rarityPie_position_y + rarityPie_size / 2 + 18)],
                              "(共{}件)".format(weapon_popularMWSampleNum_fullNum),
                              font=ImageFont.truetype(self.font_path_taipei, size=rarityPie_text_size),
                              anchor="mm", fill="#ff7d00")

        # 绘制玩家打分
        if True :
            weapon_pveRating = float(lightgg_json["pveRating"])
            weapon_pvpRating = float(lightgg_json["pvpRating"])

            ratingPie_size = 100
            ratingPie_position_x = 760
            ratingPie_position_y = 20
            ratingPie_text_size = 10
            color_pve = (45, 94, 196)
            color_pvp = (167, 24, 28)

            draw.arc([self.grv(ratingPie_position_x),
                      self.grv(ratingPie_position_y),
                      self.grv(ratingPie_position_x + ratingPie_size),
                      self.grv(ratingPie_position_y + ratingPie_size)],
                     start=0, end=360,
                     width=self.grv(0.01), fill=gray)
            # 画pve评分弧(左半)
            draw.arc([self.grv(ratingPie_position_x),
                      self.grv(ratingPie_position_y),
                      self.grv(ratingPie_position_x + ratingPie_size),
                      self.grv(ratingPie_position_y + ratingPie_size)],
                     start=90, end=weapon_pveRating/5*180+90,
                     width=self.grv(0.01), fill=color_pve)
            # 画pvp评分弧(右半)
            draw.arc([self.grv(ratingPie_position_x),
                      self.grv(ratingPie_position_y),
                      self.grv(ratingPie_position_x + ratingPie_size),
                      self.grv(ratingPie_position_y + ratingPie_size)],
                     start=-weapon_pvpRating/5*180+90, end=90,
                     width=self.grv(0.01), fill=color_pvp)
            # 画上下的两个分割线
            draw.arc([self.grv(ratingPie_position_x),
                      self.grv(ratingPie_position_y),
                      self.grv(ratingPie_position_x + ratingPie_size),
                      self.grv(ratingPie_position_y + ratingPie_size)],
                     start=90, end=91,
                     width=self.grv(0.01))
            draw.arc([self.grv(ratingPie_position_x),
                      self.grv(ratingPie_position_y),
                      self.grv(ratingPie_position_x + ratingPie_size),
                      self.grv(ratingPie_position_y + ratingPie_size)],
                     start=-91, end=-90,
                     width=self.grv(0.01))
            # 放置logo
            pve_icon = Image.open("./mediaDataBase/custom/icon/pve-icon.png")
            pvp_icon = Image.open("./mediaDataBase/custom/icon/pvp-icon.png")
            pve_icon = pve_icon.resize(self.grvl(41*0.5, 49*0.5), resample=Image.Resampling.LANCZOS)
            pvp_icon = pvp_icon.resize(self.grvl(47*0.5, 47*0.5), resample=Image.Resampling.LANCZOS)
            canvas.paste(pve_icon, self.grvl(ratingPie_position_x+25, rarityPie_position_y+25), mask=pve_icon.convert("RGBA"))
            canvas.paste(pvp_icon, self.grvl(ratingPie_position_x+55, rarityPie_position_y+25), mask=pvp_icon.convert("RGBA"))
            # 写玩家评分
            draw.text(self.grvl(ratingPie_position_x+48, rarityPie_position_y+65),
                      "{}分".format(weapon_pveRating),
                      font=ImageFont.truetype(self.font_path_taipei, size=13),
                      fill=color_pve, anchor="rs", stroke_fill="#ffffff", stroke_width=1)
            draw.text(self.grvl(ratingPie_position_x + 52, rarityPie_position_y + 65),
                      "{}分".format(weapon_pvpRating),
                      font=ImageFont.truetype(self.font_path_taipei, size=13),
                      fill=color_pvp, anchor="ls", stroke_fill="#ffffff", stroke_width=1)
            # 写pve和pvp注释
            draw.text(self.grvl(ratingPie_position_x + 48, rarityPie_position_y + 80),
                      "PVE",
                      font=ImageFont.truetype(self.font_path_taipei, size=10),
                      fill=color_pve, anchor="rs", stroke_fill="#ffffff", stroke_width=1)
            draw.text(self.grvl(ratingPie_position_x + 52, rarityPie_position_y + 80),
                      "PVP",
                      font=ImageFont.truetype(self.font_path_taipei, size=10),
                      fill=color_pvp, anchor="ls", stroke_fill="#ffffff", stroke_width=1)

        # 放一个总结武器用途的图标
        if True:
            if weapon_pveRating != 0 and weapon_pvpRating != 0:
                pve_icon = Image.open("./mediaDataBase/custom/icon/pve-icon.png")  # 414x494
                pvp_icon = Image.open("./mediaDataBase/custom/icon/pvp-icon.png")  # 443x443
                pvx_icon = Image.open("./mediaDataBase/custom/icon/pve-pvp-icon.png")  # 266x348

                if weapon_pveRating >=4.5 and weapon_pvpRating >= 4.5:
                    pvx_icon = pvx_icon.resize((int(266*100/348), 100), resample=Image.Resampling.LANCZOS)
                    canvas.paste(pvx_icon,
                                 (760-20-pvx_icon.size[0], 20),
                                 mask=pvx_icon.convert("RGBA"))

                elif weapon_pveRating > weapon_pvpRating and weapon_pveRating > 4:
                    pve_icon = pve_icon.resize((int(414 * 100 / 494), 100), resample=Image.Resampling.LANCZOS)
                    canvas.paste(pve_icon,
                                 (760 - 20 - pve_icon.size[0], 20),
                                 mask=pve_icon.convert("RGBA"))

                elif weapon_pvpRating > weapon_pveRating and weapon_pvpRating > 4:
                    pvp_icon = pvp_icon.resize((int(443 * 100 / 443), 100), resample=Image.Resampling.LANCZOS)
                    canvas.paste(pvp_icon,
                                 (760 - 20 - pvp_icon.size[0], 20),
                                 mask=pvp_icon.convert("RGBA"))

        # 绘制武器流行perk组合(如果有)
        if lightgg_json["popularPerkCombo"]:
            cursor = self.grvl(cursor_perk[0] + 360, cursor_perk[1])  # 指针
            cursor_perkCombo = cursor  # 指针
            perkCombo_icon_size = 28  # perk图标大小
            perkCombo_Gap_y = 44  # perk组合上下间距
            perkCombo_Gap_x = 36  # perk组合左右间距

            for index in range(len(lightgg_json["popularPerkCombo"])):
                # perkCombo流行度
                perkCombo_Popularity = float(lightgg_json["popularPerkCombo"][index]["perkPopularity"][:-1])
                if index == 0:
                    perkCombo_Popularity_max = perkCombo_Popularity
                # 加载json
                perk1_json = self.queryLocalDataBase("DestinyInventoryItemDefinition", lightgg_json["popularPerkCombo"][index]["perkHash1"])
                perk2_json = self.queryLocalDataBase("DestinyInventoryItemDefinition", lightgg_json["popularPerkCombo"][index]["perkHash2"])
                # 加载perk名字
                perk1_name = perk1_json["displayProperties"]
                perk2_name = perk2_json["displayProperties"]
                # 读取perk图标
                perk1_icon = Image.open("./mediaDataBase" + perk1_json["displayProperties"]["icon"])
                perk2_icon = Image.open("./mediaDataBase" + perk2_json["displayProperties"]["icon"])
                # 缩放
                perk1_icon = perk1_icon.resize(self.grvl(perkCombo_icon_size, perkCombo_icon_size), resample=Image.Resampling.LANCZOS)
                perk2_icon = perk2_icon.resize(self.grvl(perkCombo_icon_size, perkCombo_icon_size), resample=Image.Resampling.LANCZOS)

                # 放置图标
                canvas.paste(perk1_icon,
                             self.grvl(cursor[0], cursor[1] + perkCombo_Gap_y * index),
                             mask=perk1_icon.convert("RGBA"))
                canvas.paste(perk2_icon,
                             self.grvl(cursor[0] + perkCombo_Gap_x, cursor[1] + perkCombo_Gap_y * index),
                             mask=perk2_icon.convert("RGBA"))
                # 写+号
                draw.text(self.grvl(cursor[0] + perkCombo_Gap_x - 4,
                                    cursor[1] + perkCombo_icon_size/2 + perkCombo_Gap_y * index),
                          "+", font=ImageFont.truetype(self.font_path_taipei, size=13), anchor="mm")
                # 画流行度条
                # 颜色
                perkCombo_popularity_color = (int((1 - perkCombo_Popularity / perkCombo_Popularity_max) * 255),
                                              int(perkCombo_Popularity / perkCombo_Popularity_max * 255),
                                              0)
                # 位置
                perkComboPopularityBar_pos = self.grvl(cursor[0] + 70, cursor[1] + perkCombo_Gap_y * index - 4)
                # 画显示条
                draw.rectangle([perkComboPopularityBar_pos[0],
                                perkComboPopularityBar_pos[1] + self.grv_pixel(
                                    perkCircleSize * (1 - perkCombo_Popularity / perkCombo_Popularity_max)),
                                perkComboPopularityBar_pos[0] + self.grv(10),
                                perkComboPopularityBar_pos[1] + self.grv(perkCircleSize)],
                               fill=perkCombo_popularity_color)
                # 画外框
                draw.rectangle([perkComboPopularityBar_pos[0],
                                perkComboPopularityBar_pos[1],
                                perkComboPopularityBar_pos[0] + self.grv(10),
                                perkComboPopularityBar_pos[1] + self.grv(perkCircleSize)],
                               outline=perkCombo_popularity_color)
                # 写字
                draw.text(self.grvl(perkComboPopularityBar_pos[0] + 5,
                                    perkComboPopularityBar_pos[1] + perkCircleSize / 2),
                          "{:.0f}".format(perkCombo_Popularity),
                          font=ImageFont.truetype(self.font_path_deng, size=10),
                          anchor="mm",
                          stroke_fill="#000000", stroke_width=1)
                # 画分割线
                draw.line([cursor[0] - 2,
                           cursor[1] + (index+0.2) * perkCombo_Gap_y + perkCombo_icon_size,
                           cursor[0] + 85,
                           cursor[1] + (index+0.2) * perkCombo_Gap_y + perkCombo_icon_size],
                          fill=gray)
                # 在最下一栏写字
                if index == len(lightgg_json["popularPerkCombo"]) - 1:
                    draw.text([cursor[0] + perkCombo_icon_size + 12,
                               cursor[1] + perkCombo_Gap_y * (index + 1.3)],
                              "流行Perk组合",
                              font=ImageFont.truetype(self.font_path_sun, size=13),
                              anchor="ms")
                    draw.text([cursor[0] + perkCombo_icon_size + 12,
                               cursor[1] + perkCombo_Gap_y * (index + 1.7)],
                              "样本量:{}".format(lightgg_json["popularPerkSampleNum"]),
                              font=ImageFont.truetype(self.font_path_sun, size=12),
                              anchor="ms")

        # 绘制流行大师杰作(如果有)
        if lightgg_json["popularMW"]:
            mw_icon_size = 50
            mw_icon_gap_y = 88

            cursor = [cursor_perkCombo[0] + 130, cursor_perkCombo[1] - 4]
            cursor_mw = cursor

            # 画图标
            for index in range(len(lightgg_json["popularMW"])):
                if index == 4:
                    break

                mw_hash = lightgg_json["popularMW"][index]
                mw_json = self.queryLocalDataBase("DestinyInventoryItemDefinition", mw_hash["MWHash"], locale=locale)
                mw_icon_url = mw_json["displayProperties"]["icon"]
                loadPicture(mw_icon_url)
                mw_icon = Image.open("./mediaDataBase" + mw_icon_url)
                mw_icon = mw_icon.resize((mw_icon_size, mw_icon_size), resample=Image.Resampling.LANCZOS)
                canvas.paste(mw_icon, self.grvl(cursor[0], cursor[1] + mw_icon_gap_y * index),
                             mask=mw_icon.convert("RGBA"))
            # 写字
                mw_enhance_json = self.queryLocalDataBase("DestinyStatDefinition", mw_json["investmentStats"][0]["statTypeHash"])
                mw_name = mw_enhance_json["displayProperties"]["name"]
                draw.text(self.grvl(cursor[0] + mw_icon_size/2, cursor[1] + mw_icon_gap_y * index + mw_icon_size + 8),
                          mw_name,
                          font=defaultFont, anchor="mm")
            # 画流行度条
                mw_popularity = float(lightgg_json["popularMW"][index]["MWPopularity"][:-1])
                if index == 0:
                    mw_popularity_max = mw_popularity
                # 颜色
                mw_popularity_color = (int((1 - mw_popularity / mw_popularity_max) * 255),
                                       int(mw_popularity / mw_popularity_max * 255),
                                       0)
                # 画外边框
                draw.rectangle([self.grv(cursor[0]),
                                self.grv(cursor[1] + mw_icon_gap_y * index + mw_icon_size + 16),
                                self.grv(cursor[0] + mw_icon_size),
                                self.grv(cursor[1] + mw_icon_gap_y * index + mw_icon_size + 28)],
                               outline=mw_popularity_color)
                # 填色
                draw.rectangle([self.grv(cursor[0]),
                                self.grv(cursor[1] + mw_icon_gap_y * index + mw_icon_size + 16),
                                self.grv(cursor[0] + mw_icon_size * mw_popularity / mw_popularity_max),
                                self.grv(cursor[1] + mw_icon_gap_y * index + mw_icon_size + 28)],
                               fill=mw_popularity_color)
                # 写字
                draw.text([self.grv(cursor[0] + mw_icon_size / 2 + 1),
                           self.grv(cursor[1] + mw_icon_gap_y * index + mw_icon_size + 27)],
                          "{:.0f}%".format(mw_popularity),
                          font=ImageFont.truetype(self.font_path_sans, size=12),
                          anchor="ms",
                          stroke_width=1, stroke_fill="#000000")
                # 画分割线
                draw.line([cursor[0] - 6,
                           cursor[1] + (index + 0.39) * mw_icon_gap_y + mw_icon_size,
                           cursor[0] + mw_icon_size + 6,
                           cursor[1] + (index + 0.39) * mw_icon_gap_y + mw_icon_size],
                          fill=gray)
                # 在最下一栏写字
                if index == 3:
                    draw.text([cursor[0] + mw_icon_size / 2,
                               cursor[1] + mw_icon_gap_y * (index + 1.2)],
                              "流行MW组合",
                              font=ImageFont.truetype(self.font_path_sun, size=13),
                              anchor="ms")
                    draw.text([cursor[0] + mw_icon_size / 2,
                               cursor[1] + mw_icon_gap_y * (index + 1.39)],
                              "样本量:{}".format(lightgg_json["popularMWSampleNum"]),
                              font=ImageFont.truetype(self.font_path_sun, size=12),
                              anchor="ms")

            # 画分割线
            draw.line([self.grv(cursor[0] - 25),
                       self.grv(cursor[1] - 4),
                       self.grv(cursor[0] - 25),
                       self.grv(cursor[1] + 400)],
                      fill=gray)

        # 绘制流行模组(如果有)
        if lightgg_json["popularMod"]:
            cursor = [cursor_mw[0] +100, cursor[1]]

            mod_icon_size = 50
            mod_icon_gap_x = 75
            mod_icon_gap_y = 88

            # 遍历模组
            for index in range(len(lightgg_json["popularMod"])):
                mod_hash = lightgg_json["popularMod"][index]["modHash"]
                mod_json = self.queryLocalDataBase("DestinyInventoryItemDefinition", mod_hash, locale=locale)
                mod_name = mod_json["displayProperties"]["name"]
                mod_icon_url = mod_json["displayProperties"]["icon"]
                loadPicture(mod_icon_url)
                mod_icon = Image.open("./mediaDataBase" + mod_icon_url)
                mod_icon = mod_icon.resize(self.grvl(mod_icon_size, mod_icon_size), resample=Image.Resampling.LANCZOS)

                mod_icon_pos = (self.grv(cursor[0] + (index % 2) * mod_icon_gap_x),
                                self.grv(cursor[1] + (index // 2) * mod_icon_gap_y))

                # 粘贴图标
                canvas.paste(mod_icon,
                             mod_icon_pos,
                             mask=mod_icon.convert("RGBA"))
                # 画边框
                draw.rectangle([mod_icon_pos[0],
                                mod_icon_pos[1],
                                mod_icon_pos[0] + mod_icon_size - 1,
                                mod_icon_pos[1] + mod_icon_size - 1],
                               outline=(120, 120, 120))
                # 写mod名
                if "伊卡洛斯握把" in mod_name:
                    mod_name = mod_name[:-2]

                draw.text([mod_icon_pos[0] + mod_icon_size/2,
                           mod_icon_pos[1] + mod_icon_size + 1],
                          mod_name,
                          font=ImageFont.truetype(self.font_path_sun, size=12),
                          anchor="ma")

                # 画流行度条
                mod_popularity = float(lightgg_json["popularMod"][index]["modPopularity"][:-1])
                if index == 0:
                    mod_popularity_max = mod_popularity
                # 颜色
                mod_popularity_color = (int((1 - mod_popularity / mod_popularity_max) * 255),
                                        int(mod_popularity / mod_popularity_max * 255),
                                        0)
                # 画外边框
                draw.rectangle([self.grv(mod_icon_pos[0]),
                                self.grv(mod_icon_pos[1] + mod_icon_size + 16),
                                self.grv(mod_icon_pos[0] + mod_icon_size),
                                self.grv(mod_icon_pos[1] + mod_icon_size + 16 + 12)],
                               outline=mod_popularity_color)
                # 填色
                draw.rectangle([self.grv(mod_icon_pos[0]),
                                self.grv(mod_icon_pos[1] + mod_icon_size + 16),
                                self.grv(mod_icon_pos[0] + mod_icon_size * (mod_popularity / mod_popularity_max)),
                                self.grv(mod_icon_pos[1] + mod_icon_size + 16 + 12)],
                               fill=mod_popularity_color)
                # 写字
                draw.text([self.grv(mod_icon_pos[0] + mod_icon_size / 2 + 1),
                           self.grv(mod_icon_pos[1] + mod_icon_size + 14)],
                          "{:.0f}%".format(mod_popularity),
                          font=ImageFont.truetype(self.font_path_sans, size=12),
                          anchor="ma",
                          stroke_width=1, stroke_fill="#000000")
                # 画横向分割线
                draw.line([self.grv(mod_icon_pos[0] - 6),
                           self.grv(mod_icon_pos[1] + mod_icon_size + 34),
                           self.grv(mod_icon_pos[0] + mod_icon_size + 6),
                           self.grv(mod_icon_pos[1] + mod_icon_size + 34)],
                          fill=gray)
            # 写注释
            draw.text([self.grv(cursor[0] + mod_icon_gap_x/2 + mod_icon_size/2),
                       self.grv(cursor[1] + 4 * mod_icon_gap_y + 5)],
                      "流行模组",
                      font=ImageFont.truetype(self.font_path_sun, size=12),
                      anchor="ma")
            draw.text([self.grv(cursor[0] + mod_icon_gap_x / 2 + mod_icon_size / 2),
                       self.grv(cursor[1] + 4 * mod_icon_gap_y + 23)],
                      "样本量:{}".format(lightgg_json["popularModSampleNum"]),
                      font=ImageFont.truetype(self.font_path_sun, size=12),
                      anchor="ma")
            # 画分割线
            draw.line([self.grv(cursor[0] - 25),
                       self.grv(cursor[1] - 4),
                       self.grv(cursor[0] - 25),
                       self.grv(cursor[1] + 400)],
                      fill=gray)

        # 裁剪不必要的区域
        if True:
            if 5 <= maxPerkNum <= 8:
                maxPerkNum = 9
            if maxPerkNum >= 18 :
                maxPerkNum = 18

            canvas = canvas.crop((0,
                                  0,
                                  canvas_width,
                                  1060 - (14-maxPerkNum)*44))

        # 写一些其他的注释
        if True:
            draw = ImageDraw.Draw(canvas)
            draw.text([canvas_width - 2, canvas.size[1]],
                      "WeaponHash=" + str(self.weapon_hash) + "\n" +
                      "LightGGDataTime=" + time.asctime(time.localtime(lightggdata_time)) + "\n" +
                      "ImageGenerateTime=" + time.asctime(time.localtime(time.time())) + "\n" +
                      "Destiny2WeaponDataImageGenerator."+self.version+" By CaliFall",
                      font=ImageFont.truetype(self.font_path_sans, size=12),
                      anchor="rd", align="right")

        # 写一些参数(如果位置足够的话)
        if False:
            mes = ""
            if True:
                j = weapon_json
                if "hash" in j:
                    mes += "Hash={}\n".format(j["hash"])
                    mes += "Index={}\n".format(j["index"])
                if "loreHash" in j:
                    mes += "LoreHash={}\n".format(j["loreHash"])
                if "collectibleHash" in j:
                    mes += "CollectibleHash={}\n".format(j["collectibleHash"])
                if "itemType" in j:
                    mes += "ItemType={}\n".format(j["itemType"])
                if "itemSubType" in j:
                    mes += "ItemSubType={}\n".format(j["itemSubType"])

            font = ImageFont.truetype(self.font_path_sans, size=12)
            draw.text(self.grvl(800, 422),
                      mes,
                      font=font, anchor="la")

        # print("生成图片耗时{:.2f}秒".format(time.time() - self.startTime))  # 计时

        # canvas.show()  # 显示最终效果

        save_path = self.save_path
        ensureDirExist(save_path)

        if Path(save_path + str(self.weapon_hash) + ".png").is_file():
            os.remove(save_path + str(self.weapon_hash) + ".png")

        canvas.save(save_path + str(self.weapon_hash) + ".png")

        return 0


if __name__ == "__main__":
    WIF = WeaponInfoGenerator()
    while True:
        try:
            # WeaponInfoGenerator(2990047042)  # 继承
            # WeaponInfoGenerator(3164743584)  # 炎阳灵眼
            # WeaponInfoGenerator(3489657138)  # b筒子
            # WeaponInfoGenerator(2816212794)  # 邪恶符咒
            # WeaponInfoGenerator(1216319404)  # 命运使者(TL)
            # WeaponInfoGenerator(1833195496)  # 权杖
            # WeaponInfoGenerator(1541131350)  # 三头犬+1
            # WeaponInfoGenerator(3260753130)  # 帝喾
            # WeaponInfoGenerator(2208405142)  # telesto
            # WeaponInfoGenerator(2607304614)  # 经验证据
            # WeaponInfoGenerator(1046651176)  # 筹码
            # WeaponInfoGenerator(631439337)  # 裁决定论
            # WeaponInfoGenerator(999767358)  # 灾变
            res = WIF.generate(1046651176)
            print(res)
            sys.exit()
        except DataBaseNetworkError:
            print("nope")
        except requests.exceptions.ConnectTimeout:
            print("nope,too")
        except requests.exceptions.ConnectionError:
            print("error...")
