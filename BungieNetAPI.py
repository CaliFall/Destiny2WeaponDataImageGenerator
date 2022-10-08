#-- coding:UTF-8 --

import os
import re

import requests
import json
from urllib.parse import urlencode
import sqlite3
import time
from Errors import *
from requests.adapters import HTTPAdapter
from pathlib import Path
from lxml import etree

X_API_Key = "由于开源已隐藏"

# BungieNet地址
BungieNetRootUrl = "https://www.bungie.net"
# headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3947.100 Safari/537.36"
}

# BungieNetApi 父类与子类
class BungieNetAPI:
    def __init__(self):
        self.X_API_Key = X_API_Key
        self.API_Root_Path = "https://www.bungie.net/Platform"

        self.headers = {"X-API-Key": self.X_API_Key}
        self.timeout = (3, 5)
        self.maxRetries = 3
        self.autoRetry()

    # 自动重试
    def autoRetry(self):
        self.s = requests.session()
        self.s.mount('http://', HTTPAdapter(max_retries=self.maxRetries))
        self.s.mount('https://', HTTPAdapter(max_retries=self.maxRetries))

class App(BungieNetAPI):
    def GetBungieApplications(self):
        """
        获取 Bungie 创建的应用程序列表

        :return: https://bungie-net.github.io/multi/schema_Applications-Application.html#schema_Applications-Application
        """
        path = "/App/FirstParty/"
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

class User(BungieNetAPI):
    def GetBungieNetUserById(self, id):
        """
        按成员资格 ID 加载 bungienet 用户

        :param id: 请求的 Bungie.net 会员 ID
        :return: https://bungie-net.github.io/multi/schema_User-GeneralUser.html#schema_User-GeneralUser
        """
        path = "/User/GetBungieNetUserById/" + str(id)
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetSanitizedPlatformDisplayNames(self, membershipId):
        """
        获取链接到此成员 ID 但已清理（已筛选亵渎性语言）的所有显示名称的列表。遵守调用用户的所有可见性规则，并大量缓存

        :param membershipId: 要加载的请求成员 ID
        :return: json
        """
        path = "/User/GetSanitizedPlatformDisplayNames/" + str(membershipId)
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetCredentialTypesForTargetAccount(self, membershipId):
        """
        返回附加到请求帐户的凭据类型的列表

        :param membershipId: 用户的成员资格 ID
        :return: https://bungie-net.github.io/multi/schema_User-Models-GetCredentialTypesForAccountResponse.html#schema_User-Models-GetCredentialTypesForAccountResponse
        """
        path = "/User/GetCredentialTypesForTargetAccount/" + str(membershipId)
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetAvailableThemes(self):
        """
        返回所有可用用户主题的列表

        :return: https://bungie-net.github.io/multi/schema_Config-UserTheme.html#schema_Config-UserTheme
        """
        path = "/User/GetAvailableThemes/"
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetMembershipDataById(self, membershipId, membershipType):
        """
        返回与提供的成员资格 ID 和成员资格类型关联的帐户列表。这将包括所有链接的帐户（即使隐藏），如果提供的凭据允许

        :param membershipId: 目标用户的成员资格 ID
        :param membershipType: 提供的会员 ID 的类型
        :return: https://bungie-net.github.io/multi/schema_User-UserMembershipData.html#schema_User-UserMembershipData
        """
        path = "/User/GetMembershipsById/" + str(membershipId) + "/" + str(membershipType)
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetMembershipFromHardLinkedCredential(self, crType, credential):
        """
        获取给定凭据的任何硬链接成员身份。仅适用于公共凭据（目前仅适用于 SteamID64）。交叉保存感知

        :param crType: 凭据类型。“SteamId”是目前唯一有效的值
        :param credential: 要查找的凭据。必须是有效的蒸汽 ID64
        :return: https://bungie-net.github.io/multi/schema_User-HardLinkedUserMembership.html#schema_User-HardLinkedUserMembership
        """
        path = "/User/GetMembershipFromHardLinkedCredential/" + str(crType) + "/" + str(credential)
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def SearchByGlobalNamePost(self, page, displayNamePrefix):
        """
        给定全局显示名称的前缀，返回共享该名称的所有用户

        :param page: 您想要的结果,从零开始的页面
        :param displayNamePrefix: 昵称前缀
        :return: https://bungie-net.github.io/multi/schema_User-UserSearchResponse.html#schema_User-UserSearchResponse
        """
        path = "/User/Search/GlobalName/" + str(page)
        data = {"displayNamePrefix": displayNamePrefix}
        mes = self.s.post(self.API_Root_Path + path, json=data, headers=self.headers, timeout=self.timeout)
        return mes.json()

class Content(BungieNetAPI):
    def GetContentType(self, type):
        """
        获取描述内容的特定变体的对象

        :param type: type
        :return: https://bungie-net.github.io/multi/schema_Content-Models-ContentTypeDescription.html#schema_Content-Models-ContentTypeDescription
        """
        path = "/Content/GetContentType/" + str(type)
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetContentById(self, id, locale, head=False):
        """
        返回 id 引用的内容项

        :param id:  id
        :param locale:  locale
        :param head: false
        :return:https://bungie-net.github.io/multi/schema_Content-ContentItemPublicContract.html#schema_Content-ContentItemPublicContract
        """
        QueryPara = {
            "head": head
        }
        path = "/Content/GetContentById/" + str(id) + "/" + str(locale)
        mes = requests.get(self.API_Root_Path + path + "?" + urlencode(QueryPara), headers=self.headers,
                           timeout=self.timeout)
        return mes.json()

    def GetContentByTagAndType(self, tag, type, locale, head=False):
        """
        返回与给定标记和内容类型匹配的最新项

        :param tag: string
        :param type: string
        :param locale: string
        :param head: Not used
        :return: https://bungie-net.github.io/multi/schema_Content-ContentItemPublicContract.html#schema_Content-ContentItemPublicContract
        """
        QueryPara = {
            "head": head
        }
        path = "/Content/GetContentByTagAndType/" + str(tag) + "/" + str(type) + "/" + str(locale)
        mes = requests.get(self.API_Root_Path + path + "?" + urlencode(QueryPara), headers=self.headers,
                           timeout=self.timeout)
        return mes.json()

    def SearchContentWithText(self, locale, ctype, currentpage, searchtext, source, tag, head=False):
        """
        根据传入的查询字符串信息获取内容。提供基本的搜索和文本搜索功能

        :param locale: locale
        :param ctype: 内容类型标签：Help, News等,提供按空格分隔的多个ctype
        :param currentpage: 搜索结果的页码，从第 1 页开始
        :param searchtext: 用于搜索的字词或短语
        :param source: 对于分析，请提示触发搜索的应用部分。自选
        :param tag: 要搜索的内容上使用的标记
        :param head: Not used
        :return: https://bungie-net.github.io/multi/schema_SearchResultOfContentItemPublicContract.html#schema_SearchResultOfContentItemPublicContract
        """
        QueryPara = {
            "ctype": ctype,
            "currentpage": currentpage,
            "head": head,
            "searchtext": searchtext,
            "source": source,
            "tag": tag
        }
        path = "/Content/Search/" + str(locale)
        mes = requests.get(self.API_Root_Path + path + "?" + urlencode(QueryPara), headers=self.headers,
                           timeout=self.timeout)
        return mes.json()

    def SearchContentByTagAndType(self, locale, tag, type, currentpage, head=False, itemsperpage=0):
        """
        搜索与给定标记和内容类型匹配的内容项

        :param locale: locale
        :param tag: tag
        :param type: type
        :param currentpage: 搜索结果的页码，从第 1 页开始
        :param head: Not used
        :param itemsperpage: Not used
        :return: https://bungie-net.github.io/multi/schema_SearchResultOfContentItemPublicContract.html#schema_SearchResultOfContentItemPublicContract
        """
        QueryPara = {
            "currentpage": currentpage,
            "head": head,
            "itemsperpage": itemsperpage
        }
        path = "/Content/SearchContentByTagAndType/" + str(tag) + "/" + str(type) + "/" + str(locale)
        mes = requests.get(self.API_Root_Path + path + "?" + urlencode(QueryPara), headers=self.headers,
                           timeout=self.timeout)
        return mes.json()

    def SearchHelpArticles(self, searchtext, size):
        """
        搜索帮助文章

        :param searchtext: string
        :param size: string
        :return: object
        """
        path = "/Content/SearchHelpArticles/" + str(searchtext) + "/" + str(size)
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

class GroupV2(BungieNetAPI):
    def GetAvailableAvatars(self):
        """
        返回已登录用户的所有可用组头像的列表

        :return: object
        """
        path = "/GroupV2/GetAvailableAvatars/"
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetAvailableThemes(self):
        """
        返回所有可用组主题的列表

        :return: https://bungie-net.github.io/multi/schema_Config-GroupTheme.html#schema_Config-GroupTheme
        """
        path = "/GroupV2/GetAvailableThemes/"
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetGroup(self, groupId):
        """
        获取有关给定 ID 的特定组的信息

        :param groupId: 请求的组的 ID
        :return: https://bungie-net.github.io/multi/schema_GroupsV2-GroupResponse.html#schema_GroupsV2-GroupResponse
        """
        path = "/GroupV2/" + str(groupId)
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetGroupByName(self, groupName, groupType):
        """
        获取有关具有给定名称和类型的特定组的信息

        :param groupName: 要查找的组的确切名称
        :param groupType: 要查找的组的类型(0=命运1，1=命运2)
        :return: https://bungie-net.github.io/multi/schema_GroupsV2-GroupResponse.html#schema_GroupsV2-GroupResponse
        """
        path = "/GroupV2/Name/" + str(groupName) + "/" + str(groupType)
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetGroupByNameV2(self, groupName, groupType):
        """
        获取有关具有给定名称和类型的特定组的信息。POST 版本

        :param groupName: 要查找的组的确切名称
        :param groupType: 要查找的组的类型(0=命运1，1=命运2)
        :return: https://bungie-net.github.io/multi/schema_GroupsV2-GroupResponse.html#schema_GroupsV2-GroupResponse
        """
        path = "/GroupV2/NameV2/"
        data = {
            "groupName": groupName,
            "groupType": groupType
        }
        mes = requests.post(self.API_Root_Path + path, json=data, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetGroupOptionalConversations(self, groupId):
        """
        获取可用可选对话频道及其设置的列表

        :param groupId: 请求的组的 ID
        :return: https://bungie-net.github.io/multi/schema_GroupsV2-GroupOptionalConversation.html#schema_GroupsV2-GroupOptionalConversation
        """
        path = "/GroupV2/" + str(groupId) + "/OptionalConversations/"
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetMembersOfGroup(self, groupId, memberType=None, nameSearch=""):
        """
        获取给定组中的成员列表

        :param groupId: 组的 ID
        :param currentpage: 页码（从 1 开始）。每页的固定大小为每页 50 个项目(未使用)
        :param memberType: 筛选出其他成员类型。对所有成员使用“null”
        :param nameSearch: 应对其对具有匹配的显示名称或唯一名称的成员执行搜索的名称片段
        :return: https://bungie-net.github.io/multi/schema_SearchResultOfGroupMember.html#schema_SearchResultOfGroupMember
        """
        path = "/GroupV2/" + str(groupId) + "/Members/"
        QueryPara = {
            "memberType": memberType,
            "nameSearch": nameSearch
        }
        mes = requests.get(self.API_Root_Path + path + "?" + urlencode(QueryPara), headers=self.headers,
                           timeout=self.timeout)
        return mes.json()

    def GetAdminsAndFounderOfGroup(self, groupId):
        """
        获取给定组中管理员级别或更高级别的成员列表

        :param groupId: 组的 ID
        :return: https://bungie-net.github.io/multi/schema_SearchResultOfGroupMember.html#schema_SearchResultOfGroupMember
        """
        path = "/GroupV2/" + str(groupId) + "/AdminsAndFounder/"
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetGroupsForMember(self, membershipType, membershipId, groupType, filter=0):
        """
        获取有关给定成员已加入的组的信息

        :param membershipType: 提供的成员资格 ID 的成员身份类型
        :param membershipId: 要为其查找已建立组的成员资格 ID
        :param filter: 过滤器应用于已加入组的列表(0)
        :param groupType: 提供的成员成立的组的类型(0=命运1,1=命运2)
        :return: https://bungie-net.github.io/multi/schema_GroupsV2-GetGroupsForMemberResponse.html#schema_GroupsV2-GetGroupsForMemberResponse
        """
        path = "/GroupV2/User/" + str(membershipType) + "/" + str(membershipId) + "/" + str(filter) + "/" + str(
            groupType)
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def RecoverGroupForFounder(self, membershipType, membershipId, groupType):
        """
        允许创始人手动恢复他们可以在游戏中看到的组，但不能在 bungie.net(存疑

        :param membershipType: 提供的成员资格 ID 的成员身份类型
        :param membershipId: 要为其查找已建立组的成员资格 ID
        :param groupType: 提供的成员成立的组的类型
        :return: https://bungie-net.github.io/multi/schema_GroupsV2-GroupMembershipSearchResponse.html#schema_GroupsV2-GroupMembershipSearchResponse
        """
        path = "/GroupV2/Recover/" + str(membershipType) + "/" + str(membershipId) + "/" + str(groupType)
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetPotentialGroupsForMember(self, membershipType, membershipId, groupType, filter=0):
        """
        获取有关给定成员已申请或受邀加入的组的信息

        :param membershipType: 提供的成员资格 ID 的成员身份类型
        :param membershipId: 要为其查找已应用组的成员 ID
        :param filter: 过滤器应用于潜在加入的组列表
        :param groupType: 所提供成员应用的组的类型
        :return:https://bungie-net.github.io/multi/schema_GroupsV2-GroupPotentialMembershipSearchResponse.html#schema_GroupsV2-GroupPotentialMembershipSearchResponse
        """
        path = "/GroupV2/User/Potential/" + str(membershipType) + "/" + str(membershipId) + "/" + str(
            filter) + "/" + str(groupType)
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

class Tokens(BungieNetAPI):
    def GetBungieRewardsList(self):
        """
        返回当前Bungie奖励的列表

        :return: https://bungie-net.github.io/multi/schema_Tokens-BungieRewardDisplay.html#schema_Tokens-BungieRewardDisplay
        """
        path = "/Tokens/Rewards/BungieRewards/"
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

class Destiny2(BungieNetAPI):
    def GetDestinyManifest(self):
        """
        将清单的当前版本作为 json 对象返回

        :return: https://bungie-net.github.io/multi/schema_Destiny-Config-DestinyManifest.html#schema_Destiny-Config-DestinyManifest
        """
        path = "/Destiny2/Manifest/"
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetDestinyEntityDefinition(self, entityType, hashIdentifier):
        """
        返回给定类型和哈希标识符的实体的静态定义。检查 API 文档中是否有具有自己定义的实体的类型名称。请注意，返回类型将始终*继承自*DestinyDefinition，但返回的特定类型将是请求的实体类型（如果可以找到）。如果您需要大量数据，请不要将其用作 Manifest 数据库的聊天替代方案，但对于简单和一次性访问，这应该很方便

        :param entityType: 您希望其获得结果的实体的类型。这些对应于实体的定义协定名称。例如，如果您正在查找项目，则此属性应为“DestinyInventoryItemDefinition”。预览：此端点仍处于测试阶段，可能会遇到粗糙的边缘。架构暂时处于最终形式，但可能存在阻止所需操作的错误
        :param hashIdentifier:要返回的特定实体的哈希标识符
        :return:https://bungie-net.github.io/multi/schema_Destiny-Definitions-DestinyDefinition.html#schema_Destiny-Definitions-DestinyDefinition
        """
        path = "/Destiny2/Manifest/" + str(entityType) + "/" + str(hashIdentifier)
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def SearchDestinyPlayerByBungieName(self, membershipType, displayName, displayNameCode):
        """
        返回给定全局 Bungie 显示名称的命运成员身份列表。此方法将隐藏由于交叉保存而被覆盖的成员身份

        :param membershipType: 有效的非 BungieNet 会员类型，或全部。指示要返回的成员身份。您可能希望将此设置为“All”
        :return: https://bungie-net.github.io/multi/schema_User-UserInfoCard.html#schema_User-UserInfoCard
        """
        path = "/Destiny2/SearchDestinyPlayerByBungieName/" + str(membershipType)
        data = {
            "displayName": displayName,
            "displayNameCode": displayNameCode
        }
        mes = requests.post(self.API_Root_Path + path, json=data, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetLinkedProfiles(self, membershipType, membershipId, getAllMemberships=True):
        """
        返回有关链接到请求成员类型/成员 ID 且具有有效 Destiny 信息的所有配置文件的摘要信息。传入的会员类型/会员ID可以是 Bungie.Net 会员资格或命运会员资格。它只返回最少量的数据来开始提出更实质性的请求，但希望能为那些只关心命运数据的人提供有用的替代用户服务。请注意，它只会返回允许您查看其链接的链接帐户

        :param membershipType: 要返回其链接的 Destiny 帐户的成员身份的类型
        :param membershipId: 您要返回其关联 Destiny 帐户的会员资格的 ID。确保您的会员ID与其会员类型相匹配：不要向我们传递PSN会员ID和XBox会员类型，这是行不通的！
        :param getAllMemberships: （可选）如果设置为“true”，则将返回所有成员资格，无论它们是否被覆盖所遮盖。无论如何，对帐户链接的正常隐私限制仍将适用
        :return: https://bungie-net.github.io/multi/schema_Destiny-Responses-DestinyLinkedProfilesResponse.html#schema_Destiny-Responses-DestinyLinkedProfilesResponse
        """
        path = "/Destiny2/" + str(membershipType) + "/Profile/" + str(membershipId) + "/LinkedProfiles"
        QueryPara = {
            "getAllMemberships": getAllMemberships
        }
        mes = requests.get(self.API_Root_Path + path + "?" + urlencode(QueryPara), headers=self.headers,
                           timeout=self.timeout)
        return mes.json()

    def GetProfile(self, membershipType, destinyMembershipId, components):
        """
        返回所提供成员资格的命运配置文件信息

        :param membershipType: 有效的非 BungieNet 会员类型
        :param destinyMembershipId: 命运会员ID
        :param components: 参阅 DestinyComponentType 枚举
        :return: https://bungie-net.github.io/multi/schema_Destiny-Responses-DestinyProfileResponse.html#schema_Destiny-Responses-DestinyProfileResponse
        """
        path = "/Destiny2/" + str(membershipType) + "/Profile/" + str(destinyMembershipId)
        QueryPara = {"components": components}
        mes = requests.get(self.API_Root_Path + path + "?" + urlencode(QueryPara), headers=self.headers,
                           timeout=self.timeout)
        return mes.json()

    def GetCharacter(self, membershipType, destinyMembershipId, characterId, components):
        """
        返回所提供字符的字符信息

        :param membershipType: 有效的非 BungieNet 会员类型
        :param destinyMembershipId: 命运会员ID
        :param characterId: 角色ID
        :param components: 参阅 DestinyComponentType 枚举
        :return:https://bungie-net.github.io/multi/schema_Destiny-Responses-DestinyCharacterResponse.html#schema_Destiny-Responses-DestinyCharacterResponse
        """
        path = "/Destiny2/" + str(membershipType) + "/Profile/" + str(destinyMembershipId) + "/Character/" + str(
            characterId)
        QueryPara = {"components": components}
        mes = requests.get(self.API_Root_Path + path + "?" + urlencode(QueryPara), headers=self.headers,
                           timeout=self.timeout)
        return mes.json()

    def GetClanWeeklyRewardState(self, groupId):
        """
        返回有关每周部落奖励的信息，以及部落是否获得奖励。请注意，这将始终将奖励报告为未兑换

        :param groupId: 战队的有效组 ID
        :return: https://bungie-net.github.io/multi/schema_Destiny-Milestones-DestinyMilestone.html#schema_Destiny-Milestones-DestinyMilestone
        """
        path = "/Destiny2/Clan/" + str(groupId) + "/WeeklyRewardState/"
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetClanBannerSource(self):
        """
        返回Clan旗帜的值字典

        :return: https://bungie-net.github.io/multi/schema_Config-ClanBanner-ClanBannerSource.html#schema_Config-ClanBanner-ClanBannerSource
        """
        path = "/Destiny2/Clan/ClanBannerDictionary/"
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetItem(self, membershipType, destinyMembershipId, itemInstanceId, components):
        """
        检索实例化命运物品的详细信息。实例化的命运项目是具有 ItemInstanceId 的项目。非实例化项目（如材质）没有有用的特定于实例的详细信息，因此无法在此处查询

        :param membershipType: 有效的非 BungieNet 会员类型
        :param destinyMembershipId: 命运档案的会员 ID
        :param itemInstanceId: 命运项的实例 ID
        :param components: 参阅 DestinyComponentType 枚举
        :return:
        """
        path = "/Destiny2/" + str(membershipType) + "/Profile/" + str(destinyMembershipId) + "/Item/" + str(
            itemInstanceId)
        QueryPara = {"components": components}
        mes = requests.get(self.API_Root_Path + path + "?" + urlencode(QueryPara), headers=self.headers,
                           timeout=self.timeout)
        return mes.json()

    def GetVendors(self, membershipType, destinyMembershipId, characterId, components, filter=0):
        """
        从可能具有轮换库存的供应商列表中获取当前可用的供应商。请注意，这不包括预览供应商和供应商即信息亭之类的东西，它们都没有轮换/动态库存。按原样使用它们的定义

        :param membershipType: 有效的非 BungieNet 会员类型
        :param destinyMembershipId: 其他用户的命运会员 ID。您可能会被拒绝
        :param characterId: 我们要为其获取供应商信息的角色的命运角色 ID
        :param components: 参阅 DestinyComponentType 枚举
        :param filter: 要返回的供应商和物料（如果有）的筛选器
        :return: https://bungie-net.github.io/multi/schema_Destiny-Responses-DestinyVendorsResponse.html#schema_Destiny-Responses-DestinyVendorsResponse
        """
        path = "/Destiny2/" + str(membershipType) + "/Profile/" + str(destinyMembershipId) + "/Character/" + str(
            characterId) + "/Vendors/"
        QueryPara = {
            "components": components,
            "filter": filter
        }
        mes = requests.get(self.API_Root_Path + path + "?" + urlencode(QueryPara), headers=self.headers,
                           timeout=self.timeout)
        return mes.json()

    def GetVendor(self, membershipType, destinyMembershipId, characterId, vendorHash, components):
        """
        获取特定供应商的详细信息

        :param membershipType: 有效的非 BungieNet 会员类型
        :param destinyMembershipId: 其他用户的命运会员 ID。您可能会被拒绝
        :param characterId: 我们要为其获取供应商信息的角色的命运角色 ID
        :param vendorHash: 要返回的供应商的哈希标识符
        :param components: 参阅 DestinyComponentType 枚举
        :return: https://bungie-net.github.io/multi/schema_Destiny-Responses-DestinyVendorResponse.html#schema_Destiny-Responses-DestinyVendorResponse
        """
        path = "/Destiny2/" + str(membershipType) + "/Profile/" + str(destinyMembershipId) + "/Character/" + str(
            characterId) + "/Vendors/" + str(vendorHash)
        QueryPara = {"components": components}
        mes = requests.get(self.API_Root_Path + path + "?" + urlencode(QueryPara), headers=self.headers,
                           timeout=self.timeout)
        return mes.json()

    def GetPublicVendors(self, components):
        """
        (预览)从供应商处获取可用物料，其中供应商有每个人共有的待售物料。如果供应商可用库存的任何部分是特定于角色或帐户的，由于可用库存的计算方式，我们将无法从此终端节点返回其数据。正如我经常说的那样：'这是一个很长的故事......

        :param components: 参阅 DestinyComponentType 枚举
        :return: https://bungie-net.github.io/multi/schema_Destiny-Responses-DestinyPublicVendorsResponse.html#schema_Destiny-Responses-DestinyPublicVendorsResponse
        """
        path = "/Destiny2/Vendors"
        QueryPara = {"components": components}
        mes = requests.get(self.API_Root_Path + path + "?" + urlencode(QueryPara), headers=self.headers,
                           timeout=self.timeout)
        return mes.json()

    def GetCollectibleNodeDetails(self, membershipType, destinyMembershipId, characterId,
                                  collectiblePresentationNodeHash, components):
        """
        给定一个将 Collectibles 作为直接后代的表示节点，这将在请求字符的上下文中返回有关这些后代的项目详细信息

        :param membershipType: 有效的非 BungieNet 会员类型
        :param destinyMembershipId: 其他用户的命运会员 ID。您可能会被拒绝
        :param characterId: 我们要为其获取可收集详细信息的角色的命运角色 ID
        :param collectiblePresentationNodeHash: 表示节点的哈希标识符，我们应为其返回可收集的详细信息。将仅返回属于此节点的直接后代的收藏品的详细信息
        :param components: 参阅 DestinyComponentType 枚举
        :return: https://bungie-net.github.io/multi/schema_Destiny-Responses-DestinyCollectibleNodeDetailResponse.html#schema_Destiny-Responses-DestinyCollectibleNodeDetailResponse
        """
        path = "/Destiny2/" + str(membershipType) + "/Profile/" + str(destinyMembershipId) + "/Character/" + str(
            characterId) + "/Collectibles/" + str(collectiblePresentationNodeHash)
        QueryPara = {"components": components}
        mes = requests.get(self.API_Root_Path + path + "?" + urlencode(QueryPara), headers=self.headers,
                           timeout=self.timeout)
        return mes.json()

    def GetPostGameCarnageReport(self, activityId):
        """
        获取活动 ID 的可用赛后屠杀报告

        :param activityId: 请求其 PGCR 的活动的 ID
        :return: https://bungie-net.github.io/multi/schema_Destiny-HistoricalStats-DestinyPostGameCarnageReportData.html#schema_Destiny-HistoricalStats-DestinyPostGameCarnageReportData
        """
        path = "/Destiny2/Stats/PostGameCarnageReport/" + str(activityId)
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetHistoricalStatsDefinition(self):
        """
        获取历史统计信息定义

        :return: https://bungie-net.github.io/multi/schema_Destiny-HistoricalStats-Definitions-DestinyHistoricalStatsDefinition.html#schema_Destiny-HistoricalStats-Definitions-DestinyHistoricalStatsDefinition
        """
        path = "/Destiny2/Stats/Definition/"
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetClanLeaderboards(self, groupId, modes, statid, maxtop=999):
        """
        (预览)获取以已登录用户的好友和提供的命运成员 Id 作为焦点的排行榜。预览：此端点仍处于测试阶段，可能会遇到粗糙的边缘。架构是最终形式，但可能存在阻止所需操作的错误

        :param groupId: 您希望获取其排行榜的战队的群组 ID
        :param maxtop: 返回的顶级玩家的最大数量。使用较大的数字获取整个排行榜
        :param modes: 要获取排行榜的游戏模式列表。有关有效值，请参阅 DestinyActivityModeType 的文档，并传入字符串表示形式（以逗号分隔）
        :param statid: 要返回的统计信息 ID，而不是返回所有排行榜统计信息
        :return: object
        """
        path = "/Destiny2/Stats/Leaderboards/Clans/" + str(groupId)
        QueryPara = {
            "maxtop": int(maxtop),
            "modes": str(modes),
            "statid": str(statid)
        }
        mes = requests.get(self.API_Root_Path + path + "?" + urlencode(QueryPara), headers=self.headers,
                           timeout=self.timeout)
        return mes.json()

    def GetClanAggregateStats(self, groupId, modes):
        """
        (预览)使用与战队排行榜相同的类别获取战队的聚合统计信息。预览：此端点仍处于测试阶段，可能会遇到粗糙的边缘。架构是最终形式，但可能存在阻止所需操作的错误

        :param groupId: 您希望获取其排行榜的战队的群组 ID
        :param modes: 要获取排行榜的游戏模式列表。有关有效值，请参阅 DestinyActivityModeType 的文档，并传入字符串表示形式（以逗号分隔）
        :return: https://bungie-net.github.io/multi/schema_Destiny-HistoricalStats-DestinyClanAggregateStat.html#schema_Destiny-HistoricalStats-DestinyClanAggregateStat
        """
        path = "/Destiny2/Stats/AggregateClanStats/" + str(groupId)
        QueryPara = {
            "modes": str(modes)
        }
        mes = requests.get(self.API_Root_Path + path + "?" + urlencode(QueryPara), headers=self.headers,
                           timeout=self.timeout)
        return mes.json()

    def GetLeaderboards(self, membershipType, destinyMembershipId, modes, statid, maxtop=999):
        """
        (预览)获取以已登录用户的好友和提供的命运成员 Id 作为焦点的排行榜。预览：此终结点尚未实现。它被返回以预览未来的功能，并用于公众意见/建议/准备

        :param membershipType: 有效的非 BungieNet 会员类型
        :param destinyMembershipId: 要检索的用户的命运成员资格Id
        :param modes: 要获取排行榜的游戏模式列表。有关有效值，请参阅 DestinyActivityModeType 的文档，并传入字符串表示形式（以逗号分隔）
        :param statid: 要返回的统计信息 ID，而不是返回所有排行榜统计信息
        :param maxtop: 返回的顶级玩家的最大数量。使用较大的数字获取整个排行榜
        :return: object
        """
        path = "/Destiny2/" + str(membershipType) + "/Account/" + str(destinyMembershipId) + "/Stats/Leaderboards/"
        QueryPara = {
            "maxtop": int(maxtop),
            "modes": str(modes),
            "statid": str(statid)
        }
        mes = requests.get(self.API_Root_Path + path + "?" + urlencode(QueryPara), headers=self.headers,
                           timeout=self.timeout)
        return mes.json()

    def GetLeaderboardsForCharacter(self, membershipType, destinyMembershipId, characterId, modes, statid, maxtop=999):
        """
        (预览)获取以已登录用户的好友和提供的命运成员 Id 作为焦点的排行榜。预览：此端点仍处于测试阶段，可能会遇到粗糙的边缘。架构是最终形式，但可能存在阻止所需操作的错误

        :param membershipType: 有效的非 BungieNet 会员类型
        :param destinyMembershipId: 要检索的用户的命运成员资格Id
        :param characterId: 为提供的命运会员资格构建排行榜的特定角色
        :param modes: 要获取排行榜的游戏模式列表。有关有效值，请参阅 DestinyActivityModeType 的文档，并传入字符串表示形式（以逗号分隔）
        :param statid: 要返回的统计信息 ID，而不是返回所有排行榜统计信息
        :param maxtop: 返回的顶级玩家的最大数量。使用较大的数字获取整个排行榜
        :return: object
        """
        path = "/Destiny2/Stats/Leaderboards/" + str(membershipType) + "/" + str(destinyMembershipId) + "/" + str(
            characterId)
        QueryPara = {
            "maxtop": int(maxtop),
            "modes": str(modes),
            "statid": str(statid)
        }
        mes = requests.get(self.API_Root_Path + path + "?" + urlencode(QueryPara), headers=self.headers,
                           timeout=self.timeout)
        return mes.json()

    def SearchDestinyEntities(self, type, searchTerm, page):
        """
        获取 Destiny 项的页面列表

        :param type: 您希望其获得结果的实体的类型。这些对应于实体的定义协定名称。例如，如果您正在查找项目，则此属性应为“DestinyInventoryItemDefinition”
        :param searchTerm: 搜索 Destiny 实体时要使用的字符串
        :param page: 要返回的页码，从 0 开始
        :return: https://bungie-net.github.io/multi/schema_Destiny-Definitions-DestinyEntitySearchResult.html#schema_Destiny-Definitions-DestinyEntitySearchResult
        """
        path = "/Destiny2/Armory/Search/" + str(type) + "/" + str(searchTerm)
        QueryPara = {
            "page": int(page)
        }
        mes = requests.get(self.API_Root_Path + path + "?" + urlencode(QueryPara), headers=self.headers,
                           timeout=self.timeout)
        return mes.json()

    def GetHistoricalStats(self, membershipType, destinyMembershipId, characterId, dayend, daystart, groups, modes,
                           periodType):
        """
        获取角色的历史统计信息

        :param membershipType: 有效的非 BungieNet 会员类型
        :param destinyMembershipId: 要检索的用户的命运成员资格Id
        :param characterId: 要检索的字符的 ID。您可以省略此字符 ID 或将其设置为 0 以获取所有字符的聚合统计信息
        :param dayend: 请求每日统计信息时返回的最后一天。使用格式 YYYY-MM-DD。目前，我们不允许在单个请求中请求超过 31 天的每日数据
        :param daystart: 请求每日统计数据的第一天返回。使用格式 YYYY-MM-DD。目前，我们不允许在单个请求中请求超过 31 天的每日数据
        :param groups: 要包含的统计信息组，否则仅返回常规统计信息。允许使用逗号分隔的列表。值： General, Weapons, Medals
        :param modes: 要返回的游戏模式。有关有效值，请参阅 DestinyActivityModeType 的文档，并传入字符串表示形式（以逗号分隔）
        :param periodType: 指示要返回的特定时间段类型。自选。可能是：每天，所有时间或活动
        :return: https://bungie-net.github.io/multi/schema_Destiny-HistoricalStats-DestinyHistoricalStatsByPeriod.html#schema_Destiny-HistoricalStats-DestinyHistoricalStatsByPeriod
        """
        path = "/Destiny2/" + str(membershipType) + "/Account/" + str(destinyMembershipId) + "/Character/" + str(
            characterId) + "/Stats/"
        QueryPara = {
            "dayend": dayend,
            "daystart": daystart,
            "groups": groups,
            "modes": modes,
            "periodType": int(periodType)
        }
        mes = requests.get(self.API_Root_Path + path + "?" + urlencode(QueryPara), headers=self.headers,
                           timeout=self.timeout)
        return mes.json()

    def GetHistoricalStatsForAccount(self, membershipType, destinyMembershipId, groups):
        """
        获取围绕给定帐户的每个字符组织的聚合历史统计信息

        :param membershipType: 帐户系统支持的成员身份类型。这是用于代替仅限内部的 Bungie.SharedDefinitions.MembershipType 的面向外部的枚举
        :param destinyMembershipId: 要检索的用户的命运成员资格Id
        :param groups: 要包含的统计信息组，否则仅返回常规统计信息。允许使用逗号分隔的列表。值： General, Weapons, Medals
        :return: https://bungie-net.github.io/multi/schema_Destiny-HistoricalStats-DestinyHistoricalStatsAccountResult.html#schema_Destiny-HistoricalStats-DestinyHistoricalStatsAccountResult
        """
        path = "/Destiny2/" + str(membershipType) + "/Account/" + str(destinyMembershipId) + "/Stats/"
        QueryPara = {
            "groups": groups
        }
        mes = requests.get(self.API_Root_Path + path + "?" + urlencode(QueryPara), headers=self.headers,
                           timeout=self.timeout)
        return mes.json()

    def GetActivityHistory(self, membershipType, destinyMembershipId, characterId, count, mode=None, page=0):
        """
        获取特定角色的活动历史记录统计信息

        :param membershipType: 帐户系统支持的成员身份类型。这是用于代替仅限内部的 Bungie.SharedDefinitions.MembershipType 的面向外部的枚举
        :param destinyMembershipId: 要检索的用户的命运成员资格Id
        :param characterId: 要检索的角色的 ID
        :param count: 要返回的行数
        :param mode: 要返回的活动模式的筛选器。None 返回所有活动。请参阅 DestinyActivityModeType 的文档以获取有效值，并传入字符串表示形式
        :param page: 要返回的页码，从 0 开始
        :return: https://bungie-net.github.io/multi/schema_Destiny-HistoricalStats-DestinyActivityHistoryResults.html#schema_Destiny-HistoricalStats-DestinyActivityHistoryResults
        """
        path = "/Destiny2/" + str(membershipType) + "/Account/" + str(destinyMembershipId) + "/Character/" + str(
            characterId) + "/Stats/Activities/"
        QueryPara = {
            "count": int(count),
            "mode": int(mode),
            "page": int(page)
        }
        mes = requests.get(self.API_Root_Path + path + "?" + urlencode(QueryPara), headers=self.headers,
                           timeout=self.timeout)
        return mes.json()

    def GetUniqueWeaponHistory(self, membershipType, destinyMembershipId, characterId):
        """
        获取有关独特武器使用情况的详细信息，包括所有异域武器

        :param membershipType: 有效的非 BungieNet 会员类型
        :param destinyMembershipId: 要检索的用户的命运成员资格Id
        :param characterId: 要检索的角色的 ID
        :return: https://bungie-net.github.io/multi/schema_Destiny-HistoricalStats-DestinyHistoricalWeaponStatsData.html#schema_Destiny-HistoricalStats-DestinyHistoricalWeaponStatsData
        """
        path = "/Destiny2/" + str(membershipType) + "/Account/" + str(destinyMembershipId) + "/Character/" + str(
            characterId) + "/Stats/UniqueWeapons/"
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetDestinyAggregateActivityStats(self, membershipType, destinyMembershipId, characterId):
        """
        获取角色参与的所有活动以及这些活动的聚合统计信息

        :param membershipType: 有效的非 BungieNet 会员类型
        :param destinyMembershipId: 要检索的用户的命运成员资格Id
        :param characterId: 应返回其活动的特定角色
        :return: https://bungie-net.github.io/multi/schema_Destiny-HistoricalStats-DestinyAggregateActivityResults.html#schema_Destiny-HistoricalStats-DestinyAggregateActivityResults
        """
        path = "/Destiny2/" + str(membershipType) + "/Account/" + str(destinyMembershipId) + "/Character/" + str(
            characterId) + "/Stats/AggregateActivityStats/"
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetPublicMilestoneContent(self, milestoneHash):
        """
        获取给定哈希里程碑的自定义本地化内容（如果存在）

        :param milestoneHash: 要返回的里程碑的标识符
        :return: https://bungie-net.github.io/multi/schema_Destiny-Milestones-DestinyMilestoneContent.html#schema_Destiny-Milestones-DestinyMilestoneContent
        """
        path = "/Destiny2/Milestones/" + str(milestoneHash) + "/Content/"
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetPublicMilestones(self):
        """
        获取有关当前可用里程碑的公开信息

        :return: https://bungie-net.github.io/multi/schema_Destiny-Milestones-DestinyPublicMilestone.html#schema_Destiny-Milestones-DestinyPublicMilestone
        """
        path = "/Destiny2/Milestones/"
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

class CommunityContent(BungieNetAPI):
    def GetCommunityContent(self, sort, mediaFilter, page):
        """
        返回社区内容

        :param sort: 排序模式
        :param mediaFilter: 要获取的媒体类型
        :param page: 从零开始的页面
        :return: https://bungie-net.github.io/multi/schema_Forum-PostSearchResponse.html#schema_Forum-PostSearchResponse
        """
        path = "/CommunityContent/Get/" + str(sort) + "/" + str(mediaFilter) + "/" + str(page)
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

class Trending(BungieNetAPI):
    def GetTrendingCategories(self):
        """
        返回 Bungie.net 趋势项目，折叠到每个类别的项目的第一页。对于类别中的分页，请调用 GetTrendingCategory

        :return:https://bungie-net.github.io/multi/schema_Trending-TrendingCategories.html#schema_Trending-TrendingCategories
        """
        path = "/Trending/Categories/"
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetTrendingCategory(self, categoryId, pageNumber):
        """
        返回某个类别的趋势项的分页列表

        :param categoryId: 要为其获取其他结果的类别的 ID
        :param pageNumber: 要返回的结果的页面
        :return: https://bungie-net.github.io/multi/schema_SearchResultOfTrendingEntry.html#schema_SearchResultOfTrendingEntry
        """
        path = "/Trending/Categories/" + str(categoryId) + "/" + str(pageNumber)
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetTrendingEntryDetail(self, trendingEntryType, identifier):
        """
        返回特定趋势条目的详细结果。请注意，趋势条目由趋势条目和标识符的组合唯一标识：标识符本身不能保证全局唯一

        :param trendingEntryType: 要返回的实体的类型
        :param identifier: 要返回的实体的标识符
        :return: https://bungie-net.github.io/multi/schema_Trending-TrendingDetail.html#schema_Trending-TrendingDetail
        """
        path = "/Trending/Details/" + str(trendingEntryType) + "/" + str(identifier)
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

class Misc(BungieNetAPI):
    def GetAvailableLocales(self):
        """
        可用本地化区域性列表

        :return: object
        """
        path = "/GetAvailableLocales/"
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetCommonSettings(self):
        """
        获取 Bungie.Net 环境使用的常用设置

        :return: https://bungie-net.github.io/multi/schema_Common-Models-CoreSettingsConfiguration.html#schema_Common-Models-CoreSettingsConfiguration
        """
        path = "/Settings/"
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetUserSystemOverrides(self):
        """
        获取应与公共系统一起遵守的特定于用户的系统覆盖

        :return: https://bungie-net.github.io/multi/schema_Common-Models-CoreSystem.html#schema_Common-Models-CoreSystem
        """
        path = "/UserSystemOverrides/"
        mes = requests.get(self.API_Root_Path + path, headers=self.headers, timeout=self.timeout)
        return mes.json()

    def GetGlobalAlerts(self, includestreaming=False):
        """
        获取任何活动的全局警报，以便在论坛横幅、帮助页面等中显示。通常用于 DOC 警报

        :param includestreaming: 确定结果中是否包含流式处理警报
        :return: https://bungie-net.github.io/multi/schema_GlobalAlert.html#schema_GlobalAlert
        """
        path = "/GlobalAlerts/"
        QueryPara = {
            "includestreaming": includestreaming
        }
        mes = requests.get(self.API_Root_Path + path + "?" + urlencode(QueryPara), headers=self.headers,
                           timeout=self.timeout)
        return mes.json()

# 读取数据库(用不上了)
'''
class DBase:
    """
    控制本地命运数据库
    数据库类型为sqlite3
    """
    def __init__(self, db_file):
        """
        初始化

        :param db_file: 命运数据库位置
        """
        self.conn = sqlite3.connect(db_file)
        self.cur = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def query(self, hashIdentifier, entityType, identifier):
        sql = "SELECT json FROM {} WHERE {} = {}"

        self.cur.execute(sql.format(entityType, identifier, hashIdentifier))
        return self.cur.fetchall()

    def getAllItemsByType(self, entityType):
        sql = "SELECT json FROM {}"

        self.cur.execute(sql.format(entityType))
        return self.cur.fetchall()
'''

# 数据库位置
'''
langDataBase = {
    "zh-chs": "./langDataBase/zh-chs/zh-chs.content",
    "en": "./langDataBase/en/en.content"
}
'''
langDataBase = {
    "zh-chs": "./langDataBase/zh-chs/zh-chs.json",
    "en": "./langDataBase/en/en.content"
}

# 自定义的快捷方法
class ShortCut:
    def __init__(self):
        # 引入API方法
        self.App = App()
        self.User = User()
        self.Content = Content()
        self.GroupV2 = GroupV2()
        self.Tokens = Tokens()
        self.Destiny2 = Destiny2()
        self.CommunityContent = CommunityContent()
        self.Trending = Trending()
        self.Misc = Misc()

        # 数据库位置
        self.langDataBase = langDataBase

        # 程序运行时缓存数据库(这样做会占用更多内存,但运行速度会大幅提升)
        self.dbCache = {}
        self.loadDataBase()

        # BungieNet地址
        self.BungieNetRootUrl = "https://www.bungie.net"

        # headers
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3947.100 Safari/537.36"
        }

    # 缓存数据库(已过时)
    '''
    def loadDataBase(self, locale=None, entityType=None):
        """
        从本地加载数据库

        :param locale: 地区
        :param entityType: 类别
        """
        # 默认加载的语言
        if locale is None:
            locale = ["zh-chs", "en"]
        # 默认加载的类型
        if entityType is None:
            entityType = ["DestinyInventoryItemDefinition", "DestinyLoreDefinition"]

        # 遍历将所需的数据库缓存
        for l in locale:
            self.dbCache[l] = {}
            with DBase(self.langDataBase[l]) as db:
                for t in entityType:
                    self.dbCache[l][t] = db.getAllItemsByType(t)
    '''

    # 缓存数据库
    def loadDataBase(self, locale=None, entityType=None):
        """
        从本地加载数据库

        :param locale: 地区
        :param entityType: 类别
        """
        # 默认加载的语言
        if locale is None:
            locale = ["zh-chs"]
        # 默认加载的类型
        if entityType is None:
            entityType = ["DestinyInventoryItemDefinition", "DestinyLoreDefinition"]

        # 遍历将所需的数据库缓存
        for l in locale:
            self.dbCache[l] = {}

            with open(langDataBase[l], "r", encoding="UTF-8") as f:
                mes = f.read()
                
            mes = json.loads(mes)

            for t in entityType:
                self.dbCache[l][t] = mes[t]

    # 通过名字搜索玩家信息
    def getPlayerInfoByName(self, prefix, postfix=None):
        """
        自定义方法,通过玩家名称获取信息

        :param prefix: 前缀
        :param postfix: 后缀(可选)
        :return: json
        """
        # 去除后缀前面的0
        if postfix is not None:
            postfix = int(str(postfix))

        # 搜索
        res = self.User.SearchByGlobalNamePost(0, str(prefix))
        results = res["Response"]["searchResults"]  # 所有的搜索结果
        result = None  # 需要的结果

        # 没有返回信息,退出
        if len(results) == 0:
            raise APILocalError("查询不到任何使用此前缀的玩家")

        # 只返回了一个玩家,则继续
        elif len(results) == 1:
            result = results[0]

        # 返回了多个玩家
        elif len(results) >= 2:
            # 如果没有输入后缀,退出
            if postfix is None:
                raise APILocalError("查询到多个玩家,请输入后缀")

            # 多页搜索比对前缀与后缀
            page = 0
            while result is None:
                if page != 0:
                    res = self.User.SearchByGlobalNamePost(page, str(prefix))
                if res["ErrorCode"] == 1:
                    results = res["Response"]["searchResults"]
                else:
                    break

                if res["ErrorCode"] != 1:
                    raise APILocalError("查询不到对应玩家")

                for x in results:
                    if x["bungieGlobalDisplayNameCode"] == postfix:
                        result = x

                page += 1

            # 如果比对之后还是没有结果,退出
            if result is None:
                raise APILocalError("查询不到对应玩家")

        # 如果程序运行到这里则意味着获得了想要的信息

        # 获得玩家的成员信息(不同平台信息)
        destinyMemberships = []
        for x in result["destinyMemberships"]:
            info = {
                "membershipTypeName": x["iconPath"][x["iconPath"].rfind("/") + 1:-8],
                "membershipType": x["membershipType"],
                "membershipId": x["membershipId"],
                "displayName": x["displayName"],
            }
            destinyMemberships.append(info)
        destinyMemberships.sort(key=lambda x: x["membershipType"])

        if "bungieNetMembershipId" not in result:
            result["bungieNetMembershipId"] = "null"

        # 获得玩家的跨平台游戏信息
        # 先检查玩家是否有跨平台存档覆盖情况
        if result["destinyMemberships"][0]["crossSaveOverride"] != 0:
            for x in result["destinyMemberships"]:
                if x["crossSaveOverride"] == x["membershipType"]:
                    crossSaveOverride = x["crossSaveOverride"]
                    membershipId = x["membershipId"]
        # 如果没有存档覆盖则默认选择最后一个平台信息(不确定这种做法是否合理)
        else:
            crossSaveOverride = result["destinyMemberships"][-1]["membershipType"]
            membershipId = result["destinyMemberships"][-1]["membershipId"]

        # 通过跨平台游戏信息查询玩家的公会信息
        res = self.GroupV2.GetGroupsForMember(crossSaveOverride, membershipId, 1)
        playerClanInfoMember = {}
        playerClanInfoGroup = {}

        # 判断玩家是否在公会中
        if res["Response"]["totalResults"] == 0:
            isPlayerInClan = False
        # 如果在公会则获取信息
        else:
            isPlayerInClan = True
            res = res["Response"]["results"][0]
            playerClanInfoMember = {
                "isOnline": res["member"]["isOnline"],
                "joinDate": res["member"]["joinDate"],
            }
            playerClanInfoGroup = {
                "groupId": res["group"]["groupId"],
                "name": res["group"]["name"],
                "creationDate": res["group"]["creationDate"],
                "modificationDate": res["group"]["modificationDate"],
                "about": res["group"]["about"],
                "memberCount": res["group"]["memberCount"],
                "isPublic": res["group"]["isPublic"],
                "motto": res["group"]["motto"],
                "locale": res["group"]["locale"],
                "clanCallsign": res["group"]["clanInfo"]["clanCallsign"]
            }

        # 整合信息
        mes = {
            "ErrorCode": 0,
            "bungieGlobalDisplayName": result["bungieGlobalDisplayName"],
            "bungieGlobalDisplayNameCode": result["bungieGlobalDisplayNameCode"],
            "bungieGlobalDisplayNameCodeFormatted": result["bungieGlobalDisplayName"] + "#" + str(result["bungieGlobalDisplayNameCode"]).zfill(4),
            "bungieNetMembershipId": result["bungieNetMembershipId"],
            "crossSaveOverride": result["destinyMemberships"][0]["crossSaveOverride"],
            # "applicableMembershipTypes": result["destinyMemberships"][0]["applicableMembershipTypes"],
            "destinyMemberships": destinyMemberships,
            "isPlayerInClan": isPlayerInClan,
            "playerClanInfo": playerClanInfoMember,
            "playerClanInfoGroup": playerClanInfoGroup
        }
        return mes

    # 通过名字搜索公会成员
    def getClanMembersByMemberName(self, prefix, postfix=None):
        """
        通过单个玩家获得整个公会的名单

        :param prefix: 前缀
        :param postfix: 后缀(可选)
        :return: list
        """
        # 搜索
        res = self.getPlayerInfoByName(prefix, postfix)
        # 如果报错就退出
        if res["ErrorCode"] != 0:
            return {
                "ErrorCode": 1,
                "Message": res["Message"]
            }

        # 如果玩家不在公会中,退出
        elif not res["isPlayerInClan"]:
            return {
                "ErrorCode": 2,
                "Message": "玩家不在任何公会中"
            }

        # 其他情况,获取玩家公会成员列表,返回一个数组
        else:
            res = self.GroupV2.GetMembersOfGroup(res["playerClanInfoGroup"]["groupId"])
            mesList = []
            for x in res["Response"]["results"]:
                mes = {
                    "memberType": x["memberType"],
                    "isOnline": x["isOnline"],
                    "membershipType": x["destinyUserInfo"]["membershipType"],
                    "membershipId": x["destinyUserInfo"]["membershipId"],
                    "displayName": x["destinyUserInfo"]["displayName"],
                    "bungieGlobalDisplayName": x["destinyUserInfo"]["bungieGlobalDisplayName"],
                    "bungieGlobalDisplayNameCode": x["destinyUserInfo"]["bungieGlobalDisplayNameCode"],
                    "joinDate": x["joinDate"]
                }
                mesList.append(mes)
            return mesList

    # 通过值搜索数据库
    def searchLocalDataBase(self, entityType, clueTagList, clue, locale="zh-chs"):
        """
        通过指定的标签路径搜索数据库

        :param entityType: 实体类型
        :param clueTagList: 标签路径
        :param clue: 线索
        :param locale: 语言
        :return: object, timeGap
        """
        # 开始计时
        timeStart = time.time()
        items = self.dbCache[locale][entityType]
        # 遍历
        for item in items:
            item = json.loads(item[0])

            # 通过线索列表获得键
            key = item
            for tag in clueTagList:
                if tag in key:
                    key = key[tag]
            # 比对键值和线索
            if key == clue:
                timeGap = time.time() - timeStart
                return item, timeGap
        # 未搜索到
        return None, 0

    # 通过武器名搜索数据库
    def searchLocalDataBaseForWeapon(self, weaponName, locale="zh-chs"):
        """
        通过指定的标签路径搜索数据库

        :param weaponName: 要搜索的武器名称
        :param locale: 语言
        :return: object, timeGap
        """
        # 开始计时
        timeStart = time.time()
        # 实体类别为DestinyInventoryItemDefinition
        items = self.dbCache[locale]["DestinyInventoryItemDefinition"]
        for item in items:
            item = json.loads(item[0])
            # 如果是武器且名称对应,则返回object和搜索时间
            if item["itemType"] == 3 and item["displayProperties"]["name"] == str(weaponName):
                timeGap = time.time() - timeStart  # 结束计时
                return item, timeGap
        # 未搜索到
        return None, 0

    # 通过武器名搜索数据库(模糊)
    def searchLocalDataBaseForWeaponBetter(self, clue, locale="zh-chs"):
        """
        通过指定的标签路径搜索数据库(模糊)

        :param weaponName: 要搜索的武器名称
        :param locale: 语言
        :return: object, timeGap
        """
        # 开始计时
        timeStart = time.time()

        # 实体类别为DestinyInventoryItemDefinition
        items = self.dbCache[locale]["DestinyInventoryItemDefinition"]

        # 设置排除列表
        filterList = ["(", ")", "-", "（", "）", "_", "."]

        # 把输入的枪名统一化
        clue = list(clue)
        for index in range(len(clue)):
            if clue[index] in filterList:
                clue[index] = ""
        clue = "".join(clue)
        clue = clue.lower()

        possibleList = []  # 模糊结果

        # 第一遍检索(只匹配100%正确的)
        for item in items:
            item = json.loads(item[0])
            # 首先跳过非武器
            if item["itemType"] != 3:
                continue

            # 统一化武器名
            weaponName = item["displayProperties"]["name"]
            weaponName = list(weaponName)
            for index in range(len(weaponName)):
                if weaponName[index] in filterList:
                    weaponName[index] = ""
            weaponName = "".join(weaponName)
            weaponName = weaponName.lower()

            # 如果找到名字一模一样的就返回
            if weaponName == clue:
                timeGap = time.time() - timeStart  # 结束计时
                return item, timeGap

            # 如果线索出现在武器名里就压入列表
            if len(clue) >= 2:
                for index in range(len(clue)):
                    # 检测到不符合就跳出
                    if clue[index] not in weaponName:
                        break
                    # 如果线索里的所有字都出现在武器名称中
                    if clue[index] in weaponName and index == len(clue) - 1:
                        possibleList.insert(0, item)

        # 如果有可疑对象则返回
        if len(possibleList) != 0:
            timeGap = time.time() - timeStart  # 结束计时
            possibleList.sort(key=lambda x: x["displayProperties"]["name"], reverse=False)
            return possibleList[0], timeGap

        # 未搜索到
        return None, 0

    # 通过前缀后缀搜索玩家
    def searchPlayer(self, prefix, postfix=None):
        """
        自定义方法,通过玩家名称获取信息

        :param prefix: 前缀
        :param postfix: 后缀(可选)
        :return: json
        """
        # 去除后缀前面的0
        if postfix is not None:
            postfix = int(str(postfix))

        # 搜索
        res = self.User.SearchByGlobalNamePost(0, str(prefix))
        results = res["Response"]["searchResults"]  # 所有的搜索结果
        result = None  # 需要的结果

        # 没有返回信息,退出
        if len(results) == 0:
            raise APILocalError("查询不到任何使用此前缀的玩家")

        # 只返回了一个玩家,则继续
        elif len(results) == 1:
            result = results[0]

        # 返回了多个玩家
        elif len(results) >= 2:
            # 如果没有输入后缀,退出
            if postfix is None:
                raise APILocalError("查询到多个玩家,请输入后缀")

            # 多页搜索比对前缀与后缀
            page = 0
            while result is None:
                if page != 0:
                    res = self.User.SearchByGlobalNamePost(page, str(prefix))
                if res["ErrorCode"] == 1:
                    results = res["Response"]["searchResults"]
                else:
                    break

                if res["ErrorCode"] != 1:
                    raise APILocalError("查询不到对应玩家")

                for x in results:
                    if x["bungieGlobalDisplayNameCode"] == postfix:
                        result = x

                page += 1

            # 如果比对之后还是没有结果,退出
            if result is None:
                raise APILocalError("查询不到对应玩家")

        # 如果程序运行到这里则意味着获得了想要的信息
        return result

    # 通过destinyMemberships获取跨平台存档覆盖和平台id
    def getMembershipDict(self, searchResult):
        resDict = {
                    "crossSaveOverride": searchResult["destinyMemberships"][0]["crossSaveOverride"],
                    "memberships": {}
        }
        for x in searchResult["destinyMemberships"]:
            resDict["memberships"][str(x["membershipType"])] = x["membershipId"]
        return resDict


# 下载最新的json文件
def downloadJsonWorld(locale="zh-chs"):
    API = Destiny2()
    res = API.GetDestinyManifest()
    url = BungieNetRootUrl + res["Response"]["jsonWorldContentPaths"][locale]
    mes = requests.get(url, headers=headers)
    mes = mes.text.encode('utf-8').decode('utf-8')
    print("downloaded")
    with open("./langDataBase/" + locale + "/" + locale + ".json", "w+", encoding="UTF-8") as f:
        f.write(mes)
    print("write finished")

# 配合检索数据库的函数,不清楚实际用途(用不上了)
def twos_comp_32(val):
    """
    数据库函数,暂不清楚用途

    :param val: 值
    :return: 值
    """
    val = int(val)
    if (val & (1 << (32 - 1))) != 0:
        val = val - (1 << 32)
    return val

# 通过hash调取数据库数据(过时)
'''
def queryLocalDataBase(entityType, hashIdentifier, locale="zh-chs"):
    if entityType == 'DestinyHistoricalStatsDefinition':
        hashIdentifier = '"{}"'.format(hashIdentifier)
        identifier = 'key'
    else:
        hashIdentifier = twos_comp_32(hashIdentifier)
        identifier = "id"

    with DBase(langDataBase[locale]) as db:
        try:
            res = db.query(hashIdentifier, entityType, identifier)
        except sqlite3.OperationalError as e:
            if e.args[0].startswith('no such table'):
                return "Invalid entityType: {}".format(entityType)
            else:
                raise e

        if len(res) > 0:
            return json.loads(res[0][0])
        else:
            return "No entry found with id: {}".format(hashIdentifier)
'''

# 删除字符串中的所有转义符和空格并转换为列表
def deleteEscapeChar(string):
    string = string.replace("\r", "")
    string = string.replace("\n", "")
    stringList = re.split(" ", string)
    stringListReturn = []
    for i in stringList:
        if i != "":
            stringListReturn.append(i)
    return stringListReturn

# 爬light.gg获取武器数据
def spiderLightgg(weaponHashId):
    url = "https://www.light.gg/db/zh-chs/items/"
    url += str(weaponHashId)

    # get请求，传入参数，返回结果集
    try:
        resp = requests.get(url, headers=headers, timeout=3)
    except requests.exceptions.ReadTimeout:
        raise DataBaseNetworkError("LightGG请求超时")
    # 将结果集的文本转化为树的结构
    tree = etree.HTML(resp.text)

    # 传说枪随机perk模式
    # 侧边栏信息
    pveRating = tree.xpath("/html/body/div[2]/div[3]/div[2]/div[1]/div[2]/div[2]/span/text()")[0]  # pve评分
    pvpRating = tree.xpath("/html/body/div[2]/div[3]/div[2]/div[1]/div[2]/div[3]/span/text()")[0]  # pvp评分
    try:
        communityRarity = tree.xpath("/html/body/div[2]/div[3]/div[2]/div[1]/a[2]/div/span/strong/text()")[0]  # 社区拥有率
    except IndexError:
        communityRarity = "0.0%"

    # 主栏信息
    # 流行perk组合数据
    popularPerkCombo = []
    tempPath = "/html/body/div[2]/div[3]/div[1]/div[3]/div[1]/div[6]/div"
    for i in range(100):
        try:
            index = i + 1
            perkHash1 = tree.xpath(tempPath + "/div[" + str(index) + "]/div/div[1]/ul/li[1]/div/@data-id")[0]
            perkHash2 = tree.xpath(tempPath + "/div[" + str(index) + "]/div/div[1]/ul/li[2]/div/@data-id")[0]
            perkName1 = tree.xpath(tempPath + "/div[" + str(index) + "]/div/div[2]/div[1]/text()")[0]
            perkName2 = tree.xpath(tempPath + "/div[" + str(index) + "]/div/div[2]/div[2]/text()")[0][2:]
            perkPopularity = tree.xpath(tempPath + "/div[" + str(index) + "]/div/div[3]/text()")[0]
            perkPopularity = deleteEscapeChar(perkPopularity)[0]
            # 合成为字典
            perkComboDict = {
                "perkHash1": perkHash1,
                "perkHash2": perkHash2,
                "perkName1": perkName1,
                "perkName2": perkName2,
                "perkPopularity": perkPopularity
            }
            popularPerkCombo.append(perkComboDict)
        except IndexError:
            break

    # 流行perk数据
    try:
        popularPerkSampleNum = tree.xpath("/html/body/div[2]/div[3]/div[1]/div[3]/div[1]/div[8]/div[2]/em/text()")[0]
        popularPerkSampleNum = deleteEscapeChar(popularPerkSampleNum)[2]
    except IndexError:
        popularPerkSampleNum = 0

    popularPerk = []
    tempPath = '/html/body/div[2]/div[3]/div[1]/div[3]/div[1]/div[8]/div[@id="community-average"]'
    for x in range(5):
        row = x + 1
        rowOfPerk = []
        tempPathRow = tempPath + "/ul[" + str(row) + "]"
        for y in range(100):
            try:
                index = y + 1
                # 爬取数据
                perkHash = tree.xpath(tempPathRow + "/li[" + str(index) + "]/div[3]/@data-id")[0]
                perkName = tree.xpath(tempPathRow + "/li[" + str(index) + "]/div[3]/a/img/@alt")[0]
                perkPopularity = tree.xpath(tempPathRow + "/li[" + str(index) + "]/div[1]/text()")[0]
                perkInfoDict = {
                    "perkHash": perkHash,
                    "perkName": perkName,
                    "perkPopularity": perkPopularity
                }
                rowOfPerk.append(perkInfoDict)
            except IndexError:
                break
        popularPerk.append(rowOfPerk)

    # 大师杰作数据
    try:
        temp = tree.xpath("/html/body/div[2]/div[3]/div[1]/div[3]/div[1]/div[11]/div[2]/em/strong/text()")[0]
        temp = deleteEscapeChar(temp)
        popularMWSampleNum = temp[2]
        popularMWSampleNum_fullNum = temp[4]
        popularMWSampleNum_fullPercent = temp[5][1:-1]
        if popularMWSampleNum_fullNum == "<":
            popularMWSampleNum_fullNum = "<"+temp[5]
            popularMWSampleNum_fullPercent = temp[6][1:-1]
    except IndexError:
        popularMWSampleNum = 0
        popularMWSampleNum_fullNum = 0
        popularMWSampleNum_fullPercent = 0

    tempPath = "/html/body/div[2]/div[3]/div[1]/div[3]/div[1]/div[11]/div[@id='masterwork-stats']"
    popularMW = []
    for x in range(100):
        try:
            index = x + 1
            MWHash = tree.xpath(tempPath + "/div[" + str(index) + "]/div/div[1]/ul/li/div/@data-id")[0]
            MWName = tree.xpath(tempPath + "/div[" + str(index) + "]/div/div[2]/div/text()")[0]
            MWPopularity = tree.xpath(tempPath + "/div[" + str(index) + "]/div/div[3]/text()")[0]
            MWPopularity = deleteEscapeChar(MWPopularity)[0]
            MWInfoDict = {
                "MWHash": MWHash,
                "MWName": MWName,
                "MWPopularity": MWPopularity
            }
            popularMW.append(MWInfoDict)
        except IndexError:
            break

    # 模组数据
    try:
        popularModSampleNum = tree.xpath("/html/body/div[2]/div[3]/div[1]/div[3]/div[1]/div[13]/div[1]/em/text()")[0]
        popularModSampleNum = deleteEscapeChar(popularModSampleNum)[2]
    except IndexError:
        popularModSampleNum = 0

    tempPath = "/html/body/div[2]/div[3]/div[1]/div[3]/div[1]/div[13]/div[@id='mod-stats']"
    popularMod = []
    for x in range(8):
        try:
            index = x + 1
            modHash = tree.xpath(tempPath + "/div[" + str(index) + "]/div/div[1]/ul/li/div/@data-id")[0]
            modName = tree.xpath(tempPath + "/div[" + str(index) + "]/div/div[2]/div/text()")[0]
            modPopularity = tree.xpath(tempPath + "/div[" + str(index) + "]/div/div[3]/text()")[0]
            modPopularity = deleteEscapeChar(modPopularity)[0]
            modInfoDict = {
                "modHash": modHash,
                "modName": modName,
                "modPopularity": modPopularity
            }
            popularMod.append(modInfoDict)
        except IndexError:
            break

    # 整合所有信息
    messageDict = {
        "pveRating": pveRating,
        "pvpRating": pvpRating,
        "communityRarity": communityRarity,
        "popularPerkCombo": popularPerkCombo,

        "popularPerk": popularPerk,
        "popularPerkSampleNum": popularPerkSampleNum,

        "popularMW": popularMW,
        "popularMWSampleNum": popularMWSampleNum,
        "popularMWSampleNum_fullNum": popularMWSampleNum_fullNum,
        "popularMWSampleNum_fullPercent": popularMWSampleNum_fullPercent,

        "popularMod": popularMod,
        "popularModSampleNum": popularModSampleNum
    }

    # 保证文件夹存在
    if not Path("./spiderDataBase/").is_dir():
        os.mkdir("./spiderDataBase/")
    if not Path("./spiderDataBase/lightgg").is_dir():
        os.mkdir("./spiderDataBase/lightgg")

    with open("./spiderDataBase/lightgg/"+str(weaponHashId)+".json", "w") as f:
        f.write(json.dumps(messageDict, indent=4, ensure_ascii=False))

    return messageDict

# 确保文件夹存在
def ensureDirExist(path):
    # 用正斜杠分割路径
    pathList = re.split("/", path)
    # 如果路径开头没有.则自动加一个
    if pathList[0] != ".":
        pathList.insert(0, ".")
    # 如果路径结尾不是文件名则放一个占位
    if "." not in pathList[-1]:
        pathList.append("filename")
    # 遍历检测文件夹并生成
    for i in range(len(pathList)-2):
        pathStr = "/".join(pathList[:-(len(pathList)-i-2)])
        path = Path(pathStr)
        if not path.is_dir():
            os.mkdir(pathStr)
    return 0

# 从本地加载或者下载图片
def loadPicture(url):
    # 生成本地路径
    localPathString = url
    if localPathString.startswith("."):
        localPathString = localPathString[1:]
    localPathString = "./mediaDataBase" + localPathString
    localPath = Path(localPathString)
    # 确保文件夹存在
    ensureDirExist(localPathString)

    # 如果本地存在这个文件则返回
    if localPath.is_file():
        with open(localPathString, "rb") as f:
            file = f.read()
        return file

    # 如果本地不存在则下载
    try:
        file = requests.get(BungieNetRootUrl + url, headers=headers, timeout=5)
    except requests.exceptions.ReadTimeout as e:
        raise DataBaseNetworkError("下载图片超时:{}".format(e))

    with open(localPathString, "wb") as f:
        f.write(file.content)
    return file.content


if __name__ == "__main__":
    SC = ShortCut()
    # mes = User.SearchByGlobalNamePost(0, "califall")
    # mes = SC.searchPlayer("Stud", 9030)
    mes = SC.searchPlayer("anfeng")
    # mes = SC.getClanMembersByMemberName("Stud", 9030)
    # mes = SC.getMembershipDict(SC.searchPlayer("califall", 7159))

    print(json.dumps(mes, indent=4, ensure_ascii=False))
