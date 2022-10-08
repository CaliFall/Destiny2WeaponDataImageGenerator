# Destiny2WeaponDataImageGenerator


## 一个生成命运2武器数据的程序
### 使用时需要保持网络通畅，因为程序会从bungie服务器下载图片并从Lightgg爬取数据


## 各个文件/文件夹作用如下：
### jsonDataBase文件夹: 
#### 里面存放json格式的数据库文件，此文件路径使用Destiny2.GetDestinyManifest获得
#### 可以直接点击这个链接以查询 -> https://data.destinysets.com/api/Destiny2.GetDestinyManifest
#### 其中需要的文件被收录在 “jsonWorldContentPaths” 中


### mediaDataBase文件夹:
#### 用于存放生成图片时用到的图片素材，有些图片是项目自带的，而绝大多数图片需要让程序从bungie.net自行下载


### spiderDataBase文件夹:
#### 用于存放从lightgg爬取的数据，如果你觉得数据过时，则可以手动删除来让程序重新爬取


### Error.py:
#### 自定义错误类型


### generateControl.py:
#### 用于控制程序大批量生成图片的程序，需要事先准备好需要生成的武器的hash列表文件


### generateHashList.py:
#### 用于按规则生成武器hash列表


### WeaponDataImageGeneratorBeta.py
#### 生成一张武器数据图片，实现方法是pillow

### BungieNetAPI.py
#### 包含了一些其他方法，其中API KEY由于开源已经隐藏（主要功能用不到API
