# coding:utf8
import re
from lxml import etree, html

resp1 = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=gbk" />
    <title>济南房价_济南楼市|楼盘|新房价格|楼盘地图等信息介绍_新浪乐居</title>
    <meta name="Keywords" content="济南房价,济南楼市,济南楼盘,济南新楼盘,济南房价走势,济南新房,济南楼盘地图,济南新楼盘信息" />
    <meta name="Description" content="济南房价，济南楼市、楼盘、新房价格尽在新浪乐居。提供济南最新、热门、打折、团购楼盘信息,精美户型图、楼盘地图，济南房价走势曲线，覆盖全济南的房地产楼盘数据库。" />
    <meta name="google-site-verification" content="TVYhh8iGMkLFfoPNNQIVjEJO0CkLc61Dl_Upp396xWE" />
    <meta name="robots" content="index, follow" />
    <meta name="googlebot" content="index, follow" />
    <meta http-equiv="X-UA-Compatible" content="IE=EmulateIE7" />
    <meta name="google-site-verification" content="6wVLe2-4RNv4OVwqtedEBEcaMhzgwqz6tknnv0p5qoo" />
    <!--house baidu map coordinate-->
<meta name="location" content="province=山东;city=济南;coord=117.02496706629,36.682784727161">
    <link type="text/css" rel="stylesheet"  href="http://data.house.sina.com.cn/css/201509/base.css" source="widget"/>
    <link type="text/css" rel="stylesheet"  href="http://data.house.sina.com.cn/css/201509/header_footer_common.css" source="widget"/>
    <link type="text/css" rel="stylesheet"  href="http://data.house.sina.com.cn/css/201509/city_index.css" source="widget"/>
    <link type="text/css" rel="stylesheet" href="http://cdn.leju.com/121/pcorder/css/ddorder.css">
    <style type="text/css">
        .summary .my_address:hover{color: #ff6666;}
    </style>
    <script type="text/javascript" src="http://cdn.leju.com/jQuery1.8.2.js"></script>
    <script type="text/javascript">
        (function(w){
            w.pageInfo = {
                city: "sd",
                level1_page : 'house',
                level2_page : 'top'
            }
        })(window);
    </script>
</head>
<body>
<div id="t01" class="fg"></div>
<!--  /widget/header/header.vm -->
<script type="text/javascript">
    var cityList = {"as":"\u978d\u5c71","bh":"\u5317\u6d77","bt":"\u5305\u5934","bd":"\u4fdd\u5b9a","bj":"\u5317\u4eac","ba":"\u535a\u9ccc","cz":"\u5e38\u5dde","cs":"\u957f\u6c99","cq":"\u91cd\u5e86","cc":"\u957f\u6625","dl":"\u5927\u8fde","dg":"\u4e1c\u839e","fs":"\u4f5b\u5c71","fz":"\u798f\u5dde","gx":"\u5e7f\u897f","gz":"\u5e7f\u5dde","gl":"\u6842\u6797","gy":"\u8d35\u5dde","ha":"\u54c8\u5c14\u6ee8","hi":"\u6d77\u5357","hf":"\u5408\u80a5","hz":"\u676d\u5dde","hu":"\u547c\u548c\u6d69\u7279","sd":"\u6d4e\u5357","ks":"\u6606\u5c71","kf":"\u5f00\u5c01","yn":"\u6606\u660e","ly":"\u6d1b\u9633","lz":"\u5170\u5dde","nj":"\u5357\u4eac","nc":"\u5357\u660c","nb":"\u5b81\u6ce2","nt":"\u5357\u901a","qd":"\u9752\u5c9b","qi":"\u79e6\u7687\u5c9b","sj":"\u77f3\u5bb6\u5e84","su":"\u82cf\u5dde","sh":"\u4e0a\u6d77","sa":"\u4e09\u4e9a","sz":"\u6df1\u5733","sy":"\u6c88\u9633","sc":"\u56db\u5ddd","ty":"\u592a\u539f","tj":"\u5929\u6d25","ts":"\u5510\u5c71","wu":"\u829c\u6e56","we":"\u5a01\u6d77","wx":"\u65e0\u9521","wh":"\u6b66\u6c49","xm":"\u53a6\u95e8","xz":"\u5f90\u5dde","sx":"\u897f\u5b89","yi":"\u94f6\u5ddd","yt":"\u70df\u53f0","zh":"\u73e0\u6d77","hn":"\u90d1\u5dde","zs":"\u4e2d\u5c71"};
    (function (w) {
        w.pageInfo = {
            city: "sd",
            citycode: "sd",
            column: "",
            root_url: "http://data.house.sina.com.cn"
        }
    })(window);
    var ad_js = '';
</script>
<input type="hidden" id="datacity" value="sd">
<input type="hidden" id="city_en" name="city_en" value="sd">
<input type="hidden" id="datacity_en" name="site" value="sd" >
<input type="hidden" id="citycode" name="citycode" value="sd">
<div class="header">
    <div class="wmn clearfix">
        <a href="http://sd.house.sina.com.cn" class="logo1" target="_blank">Leju logo</a>

        <div id="togglecity" class="select">
            <a class="checkBtn" href="javascript:void(0)">济南
                                <i class="arrowIco"></i>
                            </a>
                        <div id="contain" class="citypop  none">
                <div class="citypopbd">
                    <div class="searchwra">
                        <div class="clearfix">
                            <input type="text" id="city" class="inputx" placeholder="请输入城市名称"/>
                            <input type="submit" value="搜索" class="submit" id="selcity"/>
                        </div>
                    </div>
                    <div class="citylist">
                        <ul class="engNav clearfix" id="city_tab">
                            <li id="city_tab1" data-tab="#city_tab1_con" data-onclass="cur" class="cur"><a>ABCDFGH</a>
                            </li>
                            <li id="city_tab2" data-tab="#city_tab2_con" data-onclass="cur"><a>JKLNQST</a></li>
                            <li id="city_tab3" data-tab="#city_tab3_con" data-onclass="cur"><a>WXYZ</a></li>
                        </ul>
                                                                        <ul class="cityli" id="city_tab1_con">
                                                                <li>
                                        <strong>A</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/as/" target="_self">鞍山</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>B</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/bh/" target="_self">北海</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/bt/" target="_self">包头</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/bd/" target="_self">保定</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/bj/" target="_self">北京</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/ba/" target="_self">博鳌</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>C</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/cz/" target="_self">常州</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/cs/" target="_self">长沙</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/cq/" target="_self">重庆</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/cc/" target="_self">长春</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>D</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/dl/" target="_self">大连</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/dg/" target="_self">东莞</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>F</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/fs/" target="_self">佛山</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/fz/" target="_self">福州</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>G</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/gx/" target="_self">广西</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/gz/" target="_self">广州</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/gl/" target="_self">桂林</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/gy/" target="_self">贵州</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>H</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/ha/" target="_self">哈尔滨</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/hi/" target="_self">海南</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/hf/" target="_self">合肥</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/hz/" target="_self">杭州</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/hu/" target="_self">呼和浩特</a>
                                                                                                                        </li>
                                                                    </ul>
                                                                                                                    <ul class="cityli none" id="city_tab2_con">
                                                                    <li>
                                        <strong>J</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/sd/" target="_self">济南</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>K</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/ks/" target="_self">昆山</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/kf/" target="_self">开封</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/yn/" target="_self">昆明</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>L</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/ly/" target="_self">洛阳</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/lz/" target="_self">兰州</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>N</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/nj/" target="_self">南京</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/nc/" target="_self">南昌</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/nb/" target="_self">宁波</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/nt/" target="_self">南通</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>Q</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/qd/" target="_self">青岛</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/qi/" target="_self">秦皇岛</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>S</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/sj/" target="_self">石家庄</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/su/" target="_self">苏州</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/sh/" target="_self">上海</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/sa/" target="_self">三亚</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/sz/" target="_self">深圳</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/sy/" target="_self">沈阳</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/sc/" target="_self">四川</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>T</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/ty/" target="_self">太原</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/tj/" target="_self">天津</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/ts/" target="_self">唐山</a>
                                                                                                                        </li>
                                                                    </ul>
                                                                                                                        <ul class="cityli none" id="city_tab3_con">
                                                                        <li>
                                        <strong>W</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/wu/" target="_self">芜湖</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/we/" target="_self">威海</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/wx/" target="_self">无锡</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/wh/" target="_self">武汉</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>X</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/xm/" target="_self">厦门</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/xz/" target="_self">徐州</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/sx/" target="_self">西安</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>Y</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/yi/" target="_self">银川</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/yt/" target="_self">烟台</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>Z</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/zh/" target="_self">珠海</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/hn/" target="_self">郑州</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/zs/" target="_self">中山</a>
                                                                                                                        </li>
                                                                    </ul>


                                <div class="btnmorewrap">
                                    <a href="http://sd.house.sina.com.cn/cityguide/" class="btnmore" target="_blank">更多城市<em>
                                        &gt;&gt;</em></a>
                                </div>
                    </div>
                </div>
                <em class="icontri">icon</em>
            </div>
                    </div>
        <ul class="main-nav">
            <li>
                <a href="http://sd.house.sina.com.cn/news/#wt_source=nlpxx_dh1_xw" target="_blank">新闻</a>
            </li>
            <li>
                <a href="http://sd.house.sina.com.cn/exhibit/#wt_source=nlpxx_dh1_xf" target="_blank">新房</a>
            </li>
                        <li>
                <a href="http://sd.esf.sina.com.cn/?bi=tg&type=house-pc&pos=news-dh#wt_source=nlpxx_dh1_esf" target="_blank">二手房</a>
            </li>
                        <li>
                <a href="http://www.7gz.com/#wt_source=nlpxx_dh1_zx" target="_blank">装修</a>
            </li>
            <li>
                <a href="http://jiaju.sina.com.cn/#wt_source=nlpxx_dh1_jj" target="_blank">家居</a>
            </li>
            <li>
                <a href="http://fangjs.sina.com.cn/#wt_source=nlpxx_dh1_jr" target="_blank">金融</a>
            </li>
                        <li>
                <a href="http://sd.bbs.house.sina.com.cn/#wt_source=nlpxx_dh1_sq" target="_blank">社区</a>
            </li>
                    </ul>
        <ul id="userlogin" class="login-bar">
            <li class="btn-app"><i class="icon-app"></i>手机版
                <div class="l_ewmBigBox none">
                    <div class="l_erweimaBox">
                        <img src="/images/201509/buyEwm.jpg">
                        <span class="l_mt">下载“<em>乐居买房</em>”</span>
                        <span>随时随地</span>
                        <img src="/images/201509/fontImg.jpg" >
                        <i class="l_poSanjiao1"></i>
                    </div>
                </div>
            </li>

            <li class="btn-login"><a
                    href="http://my.leju.com/" target="_blank"><i
                    class="icon-user"></i>登录</a></li>
            <li class="btn-reg"><span>|</span><a href="http://my.leju.com/settings/register/indexview/" target="_blank">注册</a></li>
        </ul>
        <div id="userinfo" class="none">
            <div class="useriwrap">
                <div class="userinfo">
                    <u class="iuserhead"></u>
                    <span class="usname" id="username"></span>
                    <em><i>◇</i></em>
                    <!-- 用户名需限制字数 -->
                </div>
                <dl class="none">
                    <dd><a href="http://my.leju.com/" target="_blank">帐号设置</a></dd>
                    <dd><a href="http://f.leju.com/" target="_blank">91乐居卡</a></dd>
                    <dd><a href="http://my.leju.com/center/house/index/" target="_blank">已关注的楼盘</a></dd>
                   <!--  <dd><a href="http://sd.bbs.house.sina.com.cn/bbs/space/mycollect?type=1" target="_blank">已收藏的论坛</a></dd> -->
                    <dd><a href="javascript:void(0)" id="userlogout">退出</a></dd>
                </dl>
            </div>
            <ul class="login-bar">
                <li class="btn-app"><i class="icon-app"></i>手机版
                    <div class="l_ewmBigBox none">
                        <div class="l_erweimaBox">
                            <img src="/images/201509/buyEwm.jpg">
                            <span class="l_mt">下载“<em>乐居买房</em>”</span>
                            <span>随时随地</span>
                            <img src="/images/201509/fontImg.jpg" >
                            <i class="l_poSanjiao1"></i>
                        </div>
                    </div>
                </li>
            </ul>
        </div>
    </div>
</div><!--/ /widget/header/header.vm -->

<!--  /widget/search-mod/search-mod.vm -->
<div class="search-mod" id="con_search_1">
    <div class="searchBox">
        <form method="get" action="http://data.house.sina.com.cn/sd/search#wt_source=phb_ss_ss" target="_blank">
            <div class="clearfix">
                <div class="inputBox">
                    <input type="text" class="input" placeholder="请输入楼盘名或楼盘地址" id="s00" name="keyword">
                    <input type="hidden" value="gbk" name="charset">
                     <ul class="inputList none"></ul>
                </div>
                <input type="submit" value="搜 索" class="searchBtn">
                <a href="http://data.house.sina.com.cn/sd/search_advance/#wt_source=phb_ss_gj" class="search01" target="_blank"><i class="searchAd"></i>高级搜索</a>
                <em>|</em>
                <a href="http://map.house.sina.com.cn/sd#wt_source=phb_ss_dt" class="search01" target="_blank"><i class="searchMap"></i>地图找房</a>
            </div>
            <div class="clearfix mt10">
                <select name="district">
                    <option value="0" data-init="区域">区域</option>
                                        <option value="市中">市中</option>
                                        <option value="历下">历下</option>
                                        <option value="历城">历城</option>
                                        <option value="槐荫">槐荫</option>
                                        <option value="长清区">长清区</option>
                                        <option value="天桥">天桥</option>
                                        <option value="章丘市">章丘市</option>
                                        <option value="高新区">高新区</option>
                                        <option value="济阳县">济阳县</option>
                                        <option value="商河县">商河县</option>
                                        <option value="平阴县">平阴县</option>
                                        <option value="淄博市">淄博市</option>
                                        <option value="新泰">新泰</option>
                                        <option value="海口市">海口市</option>
                                    </select>
                <select name="pricerange">
                    <option value="0" data-init="价格">价格</option>
                                        <option value="5千元以内">5千元以内</option>
                                        <option value="5千-6千元">5千-6千元</option>
                                        <option value="6千-7千元">6千-7千元</option>
                                        <option value="7千-9千元">7千-9千元</option>
                                        <option value="9千-1.1万元">9千-1.1万元</option>
                                        <option value="1.1万-1.3万元">1.1万-1.3万元</option>
                                        <option value="1.3万-1.5万元">1.3万-1.5万元</option>
                                        <option value="1.5万以上">1.5万以上</option>
                                    </select>
                <select name="housetype">
                    <option value="0" data-init="户型">户型</option>
                                        <option value="一居室">一居室</option>
                                        <option value="二居室">二居室</option>
                                        <option value="三居室">三居室</option>
                                        <option value="四居室">四居室</option>
                                        <option value="五居室">五居室</option>
                                        <option value="六居室">六居室</option>
                                        <option value="七居室">七居室</option>
                                        <option value="复式室">复式室</option>
                                        <option value="跃层">跃层</option>
                                        <option value="楼层平面图">楼层平面图</option>
                                        <option value="别墅">别墅</option>
                                    </select>
                                <select name="subway">
                    <option value="0" data-init="地铁">地铁</option>
                                        <option value="BRT1号线">BRT1号线</option>
                                        <option value="BRT2号线">BRT2号线</option>
                                        <option value="BRT3号线">BRT3号线</option>
                                        <option value="BRT4号线">BRT4号线</option>
                                        <option value="BRT5号线">BRT5号线</option>
                                        <option value="BRT6号线">BRT6号线</option>
                                    </select>
                                <select name="hometype">
                    <option value="0" data-init="类型">类型</option>
                                        <option value="60平米以下">60平米以下</option>
                                        <option value="60-90平米">60-90平米</option>
                                        <option value="90-120平米">90-120平米</option>
                                        <option value="120-140平米">120-140平米</option>
                                        <option value="140平米以上">140平米以上</option>
                                    </select>
                <select name="fitment">
                    <option value="0" data-init="装修情况">装修情况</option>
                                        <option value="一环内">一环内</option>
                                        <option value="二环内">二环内</option>
                                        <option value="二环外">二环外</option>
                                        <option value="外郊">外郊</option>
                                    </select>
                <a href="http://data.house.sina.com.cn/sd/search_advance/#wt_source=phb_xx_gd" target="_blank" class="more">更多条件>></a>
            </div>
        </form>
    </div>
</div><!--/ /widget/search-mod/search-mod.vm -->

<!--  /widget/headerNav/headerNav.vm -->
<!--  /widget/headerNav/headerNav.vm -->
<div class="headerNav">
	<div class="news-bg w clearfix">
		<div class="wrap_width clearfix">
		<div class="news-wrap01 clearfix">
			<a href="http://sd.house.sina.com.cn/exhibit#wt_source=phb_dh_100" class="new-icon" target="_blank">
				<i class="dicon01"></i>
				<span>新房中心</span>
			</a>
			<ul class="news-list clearfix">
				<li class="pb">
					<a href="http://data.house.sina.com.cn/sd/kaipan/#wt_source=phb_dh_101" target="_blank">本月开盘</a>
				</li>
				<li class="pb">
					<a href="http://data.house.sina.com.cn/sd/new/#wt_source=phb_dh_102" target="_blank">最新楼盘</a>
				</li>
				<li>
					<a href="http://data.house.sina.com.cn/sd/#wt_source=phb_dh_103" target="_blank">楼盘排行</a>
				</li>
				<li class="pb">
					<a href="http://data.house.sina.com.cn/sd/price/#wt_source=phb_dh_104" target="_blank">涨降价楼盘</a>
				</li>
			</ul>
		</div>
		<div class="news-wrap02 clearfix">
			<a href="http://sd.house.sina.com.cn/scan/#wt_source=phb_dh_200" class="new-icon" target="_blank">
				<i class="dicon02"></i>
				<span>楼盘快讯</span>
			</a>
			<ul class="news-list news-list02 clearfix">
				<li class="pb">
					<a href="http://sd.house.sina.com.cn/scan/kaipan/#wt_source=phb_dh_201" target="_blank">开盘</a>
				</li>
				<li class="pb">
					<a href="http://sd.house.sina.com.cn/scan/xinpan/#wt_source=phb_dh_202" target="_blank">新盘</a>
				</li>
				<li class="pb">
					<a href="http://sd.house.sina.com.cn/scan/dazhe/#wt_source=phb_dh_203" target="_blank">打折</a>
				</li>
				<li>
					<a href="http://sd.house.sina.com.cn/scan/daogou/#wt_source=phb_dh_204" target="_blank">导购</a>
				</li>
			</ul>
		</div>
		<div class="news-wrap03 clearfix">
			<a href="javascript:void (0);" class="new-icon">
				<i class="dicon03"></i>
				<span>乐居为您</span>
			</a>
			<ul class="news-list news-list03 clearfix">
				<li class="pb">
					<a href="http://kft.house.sina.com.cn/sd/index-1.html?ln=phb_dh_mszc" target="_blank">免费看房<span class="s_title"><i class="d_titicon"></i>专车</span></a>
				</li>
				<li class="pb">
					<a href="http://f.leju.com#wt_source=phb_dh_302" target="_blank">会员福利<span class="s_title" target="_blank"><i class="d_titicon"></i>返现</span></a>
				</li>
				<li>
					<a href="http://data.house.sina.com.cn/sd/huxing/#wt_source=phb_dh_303" target="_blank">户型推荐</a>
				</li>
				<li>
					<a href="http://data.house.sina.com.cn/sd/yangban/#wt_source=phb_dh_304" target="_blank">样板间推荐</a>
				</li>
			</ul>
		</div>
		<div class="news-wrap04 clearfix">
			<a href="http://data.house.sina.com.cn/sd/dianping/#wt_source=phb_dh_400" class="new-icon" target="_blank">
				<i class="dicon04"></i>
				<span>楼盘评测</span>
			</a>
			<ul class="news-list clearfix">
				<li class="pb">
					<a href="http://sd.house.sina.com.cn/scan/zbjf/#wt_source=phb_dh_401" target="_blank">主编荐房</a>
				</li>
				<li class="pb">
					<a href="http://data.house.sina.com.cn/sd/tujie/#wt_source=phb_dh_402" target="_blank">图解看房</a>
				</li>
				<li>
					<a href="http://sd.house.sina.com.cn/scan/kfsj/#wt_source=phb_dh_403" target="_blank">看房手记</a>
				</li>
				<li>
            						<a href="http://sd.bbs.house.sina.com.cn/owner/#wt_source=phb_dh_404" target="_blank">业主论坛</a>
            					</li>
			</ul>
		</div>
		</div>
	</div>
</div>
<!--/ /widget/headerNav/headerNav.vm --><!--/ /widget/headerNav/headerNav.vm -->

<div class="crumbs w">
    <a href="http://sd.house.sina.com.cn/#wt_source=phb_mbx_ss" class="crulist">济南房产</a>
    <em>&gt;</em>
    <a href="http://sd.house.sina.com.cn/exhibit/#wt_source=phb_mbx_ss" class="crulist">新房中心</a>
    <em>&gt;</em>
    <a href="?#wt_source=phb_mbx_ss" class="crulist">楼盘排行</a>
</div>
<div class="w clearfix">

    <!--  /widget/content_left/content_left.vm -->
    <style type="text/css">
    .house_wrap .housewrap2 .inputList {
        position: absolute;
        left: 70px;
        top: 29px;
        border: 1px solid #bfbfbf;
        width: 193px;
        background: #fff;
        z-index: 5;
    }
    .house_wrap .housewrap2 .inputList a {
        display: block;
        height: 30px;
        line-height: 32px;
        padding-left: 10px;
        font-size: 14px;
        color: #666;
    }
    .house_wrap .housewrap2 .inputList a:hover {
        background: #f2f2f2;
    }
</style>
<div class="content_left">
    <div class="ranking">
        <a href="/sd/#wt_source=phb_zphb_00" class="title">楼盘排行热榜<i class="dicon01"></i></a>
        <div class="rank">
            <h3><i class="dicon02"></i>乐居特色榜</h3>
            <ul class="rank_list clearfix">
                                <li >
                                <a href="/sd/kaipan/#wt_source=phb_tsb_01">本月开盘</a>
                                </li>
                                <li >
                                <a href="/sd/new/#wt_source=phb_tsb_02">最新楼盘</a>
                                </li>
                                <li >
                                <a href="/sd/hot/#wt_source=phb_tsb_03">热门楼盘</a>
                                </li>
                                <li >
                                <a href="/sd/?type=search_top#wt_source=phb_tsb_04">搜索热榜</a>
                                </li>
                                <li >
                                <a href="/sd/?type=monthly_clicks#wt_source=phb_tsb_05">本月不可错过</a>
                                </li>
                                <li >
                                <a href="/sd/?type=reside_3_month#wt_source=phb_tsb_06">3个月内入住</a>
                                </li>
                                <li >
                                <a href="/sd/?type=fitment_good#wt_source=phb_tsb_07">精装修</a>
                                </li>
                                <li >
                                <a href="/sd/?type=pinpai_list#wt_source=phb_tsb_08">高性价比</a>
                                </li>
                                <li >
                                <a href="/sd/?type=nearby_trackline#wt_source=phb_tsb_09">地铁沿线</a>
                                </li>
                                <li >
                                <a href="/sd/?type=edu_good#wt_source=phb_tsb_10">教育地产</a>
                                </li>
                                <li >
                                <a href="/sd/?type=region_list#wt_source=phb_tsb_11">区域列表</a>
                                </li>
                                <li >
                                <a href="/sd/?type=pinyin_list#wt_source=phb_tsb_12">拼音列表</a>
                                </li>
                                <li >
                                <a href="/sd/esf/#wt_source=phb_tsb_013">二手房小区</a>
                                </li>
                            </ul>
        </div>
        <div class="rank">
            <h3><i class="dicon03"></i>楼盘户型榜</h3>
            <ul class="rank_list clearfix">
                                <li >
                <a href="/sd/?type=rtype1#wt_source=phb_hx_01">一居</a>
                </li>
                                <li >
                <a href="/sd/?type=rtype2#wt_source=phb_hx_02">两居</a>
                </li>
                            </ul>
        </div>
        <div class="rank">
            <h3><i class="dicon04"></i>楼盘价格榜</h3>
            <ul class="rank_list clearfix">
                                <li >
                <a href="?type=pricerange&type_value=988#wt_source=phb_jg_01">5千元以内</a>
                </li>
                                <li >
                <a href="?type=pricerange&type_value=989#wt_source=phb_jg_02">5千-6千元</a>
                </li>
                                <li >
                <a href="?type=pricerange&type_value=990#wt_source=phb_jg_03">6千-7千元</a>
                </li>
                                <li >
                <a href="?type=pricerange&type_value=991#wt_source=phb_jg_04">7千-9千元</a>
                </li>
                                <li >
                <a href="/sd/?type=month_return_3k#wt_source=phb_jg_05">月供3000元以内</a>
                </li>
                            </ul>
        </div>
    </div>
        <div class="house_wrap" style="margin-top: 40px;">
        <h4>免费看房团</h4>
        <div class="housewrap2" id="bookCar_tab2">
            <input type="hidden" action="getacts" value="http://kft.house.sina.com.cn/default/api/getActivitiesForHouse?source=market&city=sd">
            <input type="hidden" action="getlines" value="http://kft.house.sina.com.cn/default/api/getActiveLinesByAid">
            <div class="kftplate_h" style="text-align:center;padding-top:50px;">
                正在为您加载看房团...
            </div>
        </div>
    </div>
        <div class="xwph">
        <div class="tit clearfix">
            <span class="floor">楼讯排行</span>
            <a target="_blank" href="http://sd.house.sina.com.cn/scan/" class="more">+ 更多</a>
        </div>
        <div class="xwmain">
            <div class="newsmain">
                <ul class="s_tim clearfix" id="dateNews">
                    <li><a data-tab="#dateNews_tab1" data-onclass="news_cur" href="#" class="news_cur">日</a></li>
                    <li><a data-tab="#dateNews_tab2" data-onclass="news_cur" href="#">周</a></li>
                    <li><a data-tab="#dateNews_tab3" data-onclass="news_cur" href="#">月</a></li>
                </ul>
            </div>
            <ul class="s_nws" id="dateNews_tab1">
                                                <li>
                                                            <i class="renum">1</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-07/19196112567152571898054.shtml#wt_source=phb_zxph_00">房价飞涨 疯抢房源......最近楼市是肿么了</a>
                </li>
                                                <li>
                                                            <i class="renum">2</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-07/19166112566312830294655.shtml#wt_source=phb_zxph_00">神奇！为什么这样的户型能降低离婚率？(图)</a>
                </li>
                                                <li>
                                                            <i class="renum">3</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-07/16546112530730724940756.shtml#wt_source=phb_zxph_00">2016各地最新房价出炉! 没有对比就没有伤害(图)</a>
                </li>
                                                <li>
                                                            <i>4</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-07/16186112521603873298686.shtml#wt_source=phb_zxph_00">新东站街区制畅想：未来生活可能会是这样的...(图)</a>
                </li>
                                                <li>
                                                            <i>5</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-03/15076111054052127463951.shtml#wt_source=phb_zxph_00">千万别惊讶 十年后房子竟然会变成这样(图)</a>
                </li>
                                                <li>
                                                            <i>6</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-07/17516112544992214178445.shtml#wt_source=phb_zxph_00">一周买房参考2.29-3.6热点楼盘推荐</a>
                </li>
                                                <li>
                                                            <i>7</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-02-29/19076110027462488677093.shtml#wt_source=phb_zxph_00">猴年探春房价篇：有的已经涨了有的即将涨价(图)</a>
                </li>
                                                <li>
                                                            <i>8</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-04/15046111415826446080928.shtml#wt_source=phb_zxph_00">济南再放大招！7日起公贷最高至70万</a>
                </li>
                                                <li>
                                                            <i>9</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-01/15556110341468726286629.shtml#wt_source=phb_zxph_00">2016年最看好这六类房子 在济南占一套就赚大了</a>
                </li>
                                                <li class="lali">
                                                            <i>10</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-08/16526112892409140795746.shtml#wt_source=phb_zxph_00">售楼处竟玩起丝袜诱惑…不说了我要去看看(图)</a>
                </li>
                            </ul>
            <ul class="s_nws none" id="dateNews_tab2">
                                                <li>
                                                            <i class="renum">1</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-08/16526112892409140795746.shtml#wt_source=phb_zxph_00">售楼处竟玩起丝袜诱惑…不说了我要去看看(图)</a>
                </li>
                                                <li>
                                                            <i class="renum">2</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-08/16596112894280832178996.shtml#wt_source=phb_zxph_00">海尔云世界二期认筹交5000享98折(图)</a>
                </li>
                                                <li>
                                                            <i class="renum">3</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-08/15436112875203715717284.shtml#wt_source=phb_zxph_00">涨价潮来袭 如何快速买到称心房(图)</a>
                </li>
                                                <li>
                                                            <i>4</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-08/17146112898084587755591.shtml#wt_source=phb_zxph_00">重汽翡翠东郡小高层交1.5万元享4万(图)</a>
                </li>
                                                <li>
                                                            <i>5</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-07/19196112567152571898054.shtml#wt_source=phb_zxph_00">房价飞涨 疯抢房源......最近楼市是肿么了</a>
                </li>
                                                <li>
                                                            <i>6</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-07/19166112566312830294655.shtml#wt_source=phb_zxph_00">神奇！为什么这样的户型能降低离婚率？(图)</a>
                </li>
                                                <li>
                                                            <i>7</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-07/16546112530730724940756.shtml#wt_source=phb_zxph_00">2016各地最新房价出炉! 没有对比就没有伤害(图)</a>
                </li>
                                                <li>
                                                            <i>8</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-07/16186112521603873298686.shtml#wt_source=phb_zxph_00">新东站街区制畅想：未来生活可能会是这样的...(图)</a>
                </li>
                                                <li>
                                                            <i>9</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-07/17516112544992214178445.shtml#wt_source=phb_zxph_00">一周买房参考2.29-3.6热点楼盘推荐</a>
                </li>
                                                <li class="lali">
                                                            <i>10</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-07/14256112493110942817223.shtml#wt_source=phb_zxph_00">祥泰城二期高层和小高层在售(图)</a>
                </li>
                            </ul>
            <ul class="s_nws none" id="dateNews_tab3">
                                                <li>
                                                            <i class="renum">1</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-08/16526112892409140795746.shtml#wt_source=phb_zxph_00">售楼处竟玩起丝袜诱惑…不说了我要去看看(图)</a>
                </li>
                                                <li>
                                                            <i class="renum">2</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-08/16596112894280832178996.shtml#wt_source=phb_zxph_00">海尔云世界二期认筹交5000享98折(图)</a>
                </li>
                                                <li>
                                                            <i class="renum">3</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-08/15436112875203715717284.shtml#wt_source=phb_zxph_00">涨价潮来袭 如何快速买到称心房(图)</a>
                </li>
                                                <li>
                                                            <i>4</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-08/17146112898084587755591.shtml#wt_source=phb_zxph_00">重汽翡翠东郡小高层交1.5万元享4万(图)</a>
                </li>
                                                <li>
                                                            <i>5</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-07/19196112567152571898054.shtml#wt_source=phb_zxph_00">房价飞涨 疯抢房源......最近楼市是肿么了</a>
                </li>
                                                <li>
                                                            <i>6</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-07/19166112566312830294655.shtml#wt_source=phb_zxph_00">神奇！为什么这样的户型能降低离婚率？(图)</a>
                </li>
                                                <li>
                                                            <i>7</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-07/16546112530730724940756.shtml#wt_source=phb_zxph_00">2016各地最新房价出炉! 没有对比就没有伤害(图)</a>
                </li>
                                                <li>
                                                            <i>8</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-07/16186112521603873298686.shtml#wt_source=phb_zxph_00">新东站街区制畅想：未来生活可能会是这样的...(图)</a>
                </li>
                                                <li>
                                                            <i>9</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-07/17516112544992214178445.shtml#wt_source=phb_zxph_00">一周买房参考2.29-3.6热点楼盘推荐</a>
                </li>
                                                <li class="lali">
                                                            <i>10</i>
                                        <a target="_blank" href="http://sd.house.sina.com.cn/scan/2016-03-07/14256112493110942817223.shtml#wt_source=phb_zxph_00">祥泰城二期高层和小高层在售(图)</a>
                </li>
                            </ul>
        </div>
    </div>
</div>    <!--/ /widget/content_left/content_left.vm -->

    <!--  /widget/summary/summary.vm -->
    <div class="summary">
        <h2 class="sumTit"><em class="none">楼盘排行热榜</em></h2>
                                          <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">本月开盘</strong>
                                        <span class="titSmall"><em class="xred">TOP 100</em></span>
                                                            <a href="/sd/kaipan/" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd107526/#wt_source=phb_01_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/a7/11/1/e49cadd62024682293aa65c9ec3_p7_mk7_osb07966_cm320X240.jpg" title="龙山郡">
                                                                                                                    <em class="rankNumRed">1</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd107526/#wt_source=phb_01_lp" class="prolink">龙山郡</a>
                                    <span class="loc">章丘市</span>
                                </p>
                            </div>
                            <p class="price">总价约<strong>200</strong>万元/套</p>
                            <p class="up_time">05月09日更新</p>
                                                        <p class="time" title="预计2016年5月 一期别墅；">开盘：预计2016年5月 一期别墅；</p>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd129715/#wt_source=phb_01_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/52/a6/3/10e5174844071cfde484715bd46_p7_mk7_os5d1a58_cm320X240.jpg" title="三箭·瑞景苑">
                                                                                                                    <em class="rankNumRed">2</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd129715/#wt_source=phb_01_lp" class="prolink">三箭·瑞景苑</a>
                                    <span class="loc">天桥</span>
                                </p>
                            </div>
                            <p class="price"><strong>7300-8400</strong>元/平米</p>
                            <p class="up_time">04月15日更新</p>
                                                        <p class="time" title="预计2016年5月 6号楼、10号楼、7号楼、8号楼、9号楼	一期开盘">开盘：预计2016年5月 6号楼、10号楼、7号楼、8号楼、9号楼	一期开盘</p>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd130540/#wt_source=phb_01_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/32/d6/2/e6e8628b3999c94d580786cc100_p7_mk7_osa2d1d8_cm320X240.jpg" title="龙泉国际广场">
                                                                                                                    <em class="rankNumRed">3</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd130540/#wt_source=phb_01_lp" class="prolink">龙泉国际广场</a>
                                    <span class="loc">章丘市</span>
                                </p>
                            </div>
                            <p class="price"><strong>待定</strong></p>
                            <p class="up_time">04月15日更新</p>
                                                        <p class="time" title="预计2016年5月开盘">开盘：预计2016年5月开盘</p>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd128840/#wt_source=phb_01_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/30/bd/c/54a78fb485de51d45ab3014735b_p7_mk7_os248792_cm320X240.jpg" title="新城·香溢紫郡">
                                                                                                                    <em class="rankNum">4</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2016378号 5号楼；济建预许2016338号 15号楼；济建预许2016221号 9号楼；济建预许2016161号 20号楼；济建预许2016065号 17号楼；济建预许2015719号 21号楼；济建预许2015718号 16号楼；济建预许2015628号 19号楼
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd128840/#wt_source=phb_01_lp" class="prolink">新城·香溢紫郡</a>
                                    <span class="loc">历城</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>6200</strong>元/平米</p>
                            <p class="up_time">05月25日更新</p>
                                                        <p class="time" title="B3地块18号楼5月22日开盘；2016年4月17日 15号楼开盘；2016年3月27日加推9号楼；2016年3月20日 20号楼开盘；2016年1月24日 17号楼开盘；2015年11月28日 21号楼2单元开盘；2015年10月31日 16号楼19号楼开盘;2016年3月份20号楼开盘">开盘：B3地块18号楼5月22日开盘；2016年4月17日 15号楼开盘；2016年3月27日加推9号楼；2016年3月20日 20号楼开盘；2016年1月24日 17号楼开盘；2015年11月28日 21号楼2单元开盘；2015年10月31日 16号楼19号楼开盘;2016年3月份20号楼开盘</p>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd114914/#wt_source=phb_01_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/81/d2/5/6b3260def9916fca70e8ef9a7b1_p7_mk7_os951a33_cm320X240.jpg" title="鑫苑世家公馆">
                                                                                                                    <em class="rankNum">5</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2014312号	4号楼  济建预许2014313号8号楼济建预许2014410号1号楼济建预许2014668号5号楼
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd114914/#wt_source=phb_01_lp" class="prolink">鑫苑世家公馆</a>
                                    <span class="loc">槐荫</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>6500</strong>元/平米</p>
                            <p class="up_time">05月04日更新</p>
                                                        <p class="time" title="2016年5月20日 二期18号楼开盘；2015-10-17加推2号楼；2015-9-12加推3号楼；2014-12	5号楼1单元2014-9-1	一期1号楼2单元共132户2014-07-05 一期4号、8号共528户">开盘：2016年5月20日 二期18号楼开盘；2015-10-17加推2号楼；2015-9-12加推3号楼；2014-12	5号楼1单元2014-9-1	一期1号楼2单元共132户2014-07-05 一期4号、8号共528户</p>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                                                <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">最新楼盘</strong>
                                        <span class="titSmall"><em class="xred">TOP 100</em></span>
                                                            <a href="/sd/new/" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd133243/#wt_source=phb_02_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/06/58/a/7936be1e5227280fea8c6489aae_p7_mk7_os6914c6_cm320X240.jpg" title="零点国际商贸物流港">
                                                                                                                    <em class="rankNumRed">1</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd133243/#wt_source=phb_02_lp" class="prolink">零点国际商贸物流港</a>
                                    <span class="loc">历城</span>
                                </p>
                            </div>
                            <p class="price"><strong>待定</strong></p>
                            <p class="up_time">01月01日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=133243" class="my_address">济南市历城区大桥路七号</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd133110/#wt_source=phb_02_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/75/d3/a/bd5f6010e9211a2f17669033c65_p7_mk7_os523a6a_cm320X240.jpg" title="联合·云东府">
                                                                                                                    <em class="rankNumRed">2</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd133110/#wt_source=phb_02_lp" class="prolink">联合·云东府</a>
                                    <span class="loc">长清区</span>
                                </p>
                            </div>
                            <p class="price"><strong>待定</strong></p>
                            <p class="up_time">01月01日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=133110" class="my_address">长清区园博园片区</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd132181/#wt_source=phb_02_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/4b/81/b/e96be934de602fa212fb5e087a1_p7_mk7_osfae3bc_cm320X240.jpg" title="华皓英伦联邦">
                                                                                                                    <em class="rankNumRed">3</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd132181/#wt_source=phb_02_lp" class="prolink">华皓英伦联邦</a>
                                    <span class="loc">高新区</span>
                                </p>
                            </div>
                            <p class="price"><strong>待定</strong></p>
                            <p class="up_time">01月01日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=132181" class="my_address">高新区舜华南路与旅游路...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd131858/#wt_source=phb_02_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/02/6f/0/c5f1c4f651f55b2b250cdc9426e_p7_mk7_os84ae07_cm320X240.jpg" title="拉菲公馆">
                                                                                                                    <em class="rankNum">4</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>6号楼 济建预许2016028号;5号楼 济建预许2016027号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd131858/#wt_source=phb_02_lp" class="prolink">拉菲公馆</a>
                                    <span class="loc">历下</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>17000</strong>元/平米</p>
                            <p class="up_time">05月04日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=131858" class="my_address">历下区CBD,省博正南转山...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd131824/#wt_source=phb_02_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/f6/83/d/48cb828a15d960e5fc144d60c1c_p7_mk7_osa93282_cm320X240.jpg" title="凤凰国际">
                                                                                                                    <em class="rankNum">5</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许：2015720；济建预许：2015721；济建预许：2016013；济建预许：2106014；济建预许：2016015
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd131824/#wt_source=phb_02_lp" class="prolink">凤凰国际</a>
                                    <span class="loc">高新区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>8700</strong>元/平米</p>
                            <p class="up_time">05月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=131824" class="my_address">旅游北路与凤凰路交汇处...</a>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                                                <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">热门楼盘</strong>
                                        <span class="titSmall"><em class="xred">TOP 100</em></span>
                                                            <a href="/sd/hot/" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd32724/#wt_source=phb_03_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/a0/b9/2/320383968bc0658792e4180c1d8_p7_mk7_os7bb278_cm320X240.jpg" title="济南鲁能领秀城">
                                                                                                                    <em class="rankNumRed">1</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015706号 中央公园东区9号楼；济建预许2015706号 中央公园东区7号楼；济建预许2015706号 中央公园东区5号楼；济建预许2015706号 中央公园东区11号楼；济建预许2015674号 中央公园东区14号楼；济建预许2015675号 中央公园东区15号楼；济建预许2015615号 中央公园东区3号楼；济建预许2015614号 中央公园东区2号楼；济建预许2015613号 中央公园东区1号楼；济建预许2015603号 中央公园东区8号楼；济建预许2015603号 中央公园东区6号楼；济建预许2015603号 中央公园东区4号楼；济建预许2015604号 中央公园东区13号楼；济建预许2015604
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd32724/#wt_source=phb_03_lp" class="prolink">济南鲁能领秀城</a>
                                    <span class="loc">市中</span>
                                </p>
                            </div>
                            <p class="price"><strong>9600-10700</strong>元/平米</p>
                            <p class="up_time">05月05日更新</p>
                                                        <p class="time">共<strong>1372219</strong>人感兴趣</p>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd34254/#wt_source=phb_03_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/19/33/d/ed3453e13794cd060bf2f60dbe0_p7_mk7_os2d2434_cm320X240.jpg" title="中海国际社区">
                                                                                                                    <em class="rankNumRed">2</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2014289号 	B4地块6号楼；济建预许2014464号 B4地块1号楼；济建预许2014465号 	B4地块3号楼；济建预许2014466号 B4地块10号楼；济建预许2014474号 B4地块20号楼；济建预许2014236号 	B4地块19号楼；济建预许2014473号 	B4地块18号楼；济建预许2014600号 B4地块17号楼
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd34254/#wt_source=phb_03_lp" class="prolink">中海国际社区</a>
                                    <span class="loc">市中</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>9400</strong>元/平米</p>
                            <p class="up_time">05月26日更新</p>
                                                        <p class="time">共<strong>372837</strong>人感兴趣</p>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd34234/#wt_source=phb_03_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/5b/48/5/21a8f1ee493282845df5e7832b1_p7_mk7_osd0296b_cm320X240.jpg" title="重汽翡翠东郡">
                                                                                                                    <em class="rankNumRed">3</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建开预许字第2013章 131-136号69号，58号楼,62#楼,63号楼,70号楼,74号楼,76号楼；济建开预许字第2012章267号68号楼；济建开预许字第2013章034号64号楼济建开预许字第2013章131号、济建开预许字第2012章267号54号楼,69号楼,55号楼5号楼，44号楼，51号楼；济建开预许字第2013
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd34234/#wt_source=phb_03_lp" class="prolink">重汽翡翠东郡</a>
                                    <span class="loc">高新区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>4500</strong>元/平米</p>
                            <p class="up_time">05月03日更新</p>
                                                        <p class="time">共<strong>319898</strong>人感兴趣</p>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd34863/#wt_source=phb_03_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/d3/8d/2/82bac70a0c139f038076bcd5a90_p7_mk7_os51ce24_cm320X240.jpg" title="恒大绿洲">
                                                                                                                    <em class="rankNum">4</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建开预许字第（2011）C0020号 20号楼；济建开预许字第（2011）C0005号 	19号楼；济建开预许字第（2011）C0004号 	18号楼；济建开预许字第（2011）C0007号 	15号楼；济建开预许字第（2011）C0002   10号楼；济建开预许字第（2011）C0012号 	B地块11号楼；济建开预许字第（20
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd34863/#wt_source=phb_03_lp" class="prolink">恒大绿洲</a>
                                    <span class="loc">长清区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>5900</strong>元/平米</p>
                            <p class="up_time">05月04日更新</p>
                                                        <p class="time">共<strong>236893</strong>人感兴趣</p>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd34219/#wt_source=phb_03_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/16/38/c/4c12d893a05d7d5578cc94ad5dc_p7_mk7_os5af536_cm320X240.jpg" title="国华东方美郡">
                                                                                                                    <em class="rankNum">5</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2011390号（611）;济建预许2011390号（617）611,615,613,617,612,616,614;济建预许2011483-486号701号楼,704号楼,703号楼,702号楼;济建预许2011389-2011390;607,601,608,605,606,603,609,604,602,610
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd34219/#wt_source=phb_03_lp" class="prolink">国华东方美郡</a>
                                    <span class="loc">市中</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>30000</strong>元/平米</p>
                            <p class="up_time">05月03日更新</p>
                                                        <p class="time">共<strong>208623</strong>人感兴趣</p>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                                                <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">搜索热榜</strong>
                                                            <a href="?type=search_top" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd32724/#wt_source=phb_04_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/a0/b9/2/320383968bc0658792e4180c1d8_p7_mk7_os7bb278_cm320X240.jpg" title="济南鲁能领秀城">
                                                                                                                    <em class="rankNumRed">1</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015706号 中央公园东区9号楼；济建预许2015706号 中央公园东区7号楼；济建预许2015706号 中央公园东区5号楼；济建预许2015706号 中央公园东区11号楼；济建预许2015674号 中央公园东区14号楼；济建预许2015675号 中央公园东区15号楼；济建预许2015615号 中央公园东区3号楼；济建预许2015614号 中央公园东区2号楼；济建预许2015613号 中央公园东区1号楼；济建预许2015603号 中央公园东区8号楼；济建预许2015603号 中央公园东区6号楼；济建预许2015603号 中央公园东区4号楼；济建预许2015604号 中央公园东区13号楼；济建预许2015604
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd32724/#wt_source=phb_04_lp" class="prolink">济南鲁能领秀城</a>
                                    <span class="loc">市中</span>
                                </p>
                            </div>
                            <p class="price"><strong>9600-10700</strong>元/平米</p>
                            <p class="up_time">05月05日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=32724" class="my_address">舜耕路与二环南路交叉口</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd34254/#wt_source=phb_04_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/19/33/d/ed3453e13794cd060bf2f60dbe0_p7_mk7_os2d2434_cm320X240.jpg" title="中海国际社区">
                                                                                                                    <em class="rankNumRed">2</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2014289号 	B4地块6号楼；济建预许2014464号 B4地块1号楼；济建预许2014465号 	B4地块3号楼；济建预许2014466号 B4地块10号楼；济建预许2014474号 B4地块20号楼；济建预许2014236号 	B4地块19号楼；济建预许2014473号 	B4地块18号楼；济建预许2014600号 B4地块17号楼
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd34254/#wt_source=phb_04_lp" class="prolink">中海国际社区</a>
                                    <span class="loc">市中</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>9400</strong>元/平米</p>
                            <p class="up_time">05月26日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=34254" class="my_address">市中北靠南二环路，由市...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd34234/#wt_source=phb_04_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/5b/48/5/21a8f1ee493282845df5e7832b1_p7_mk7_osd0296b_cm320X240.jpg" title="重汽翡翠东郡">
                                                                                                                    <em class="rankNumRed">3</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建开预许字第2013章 131-136号69号，58号楼,62#楼,63号楼,70号楼,74号楼,76号楼；济建开预许字第2012章267号68号楼；济建开预许字第2013章034号64号楼济建开预许字第2013章131号、济建开预许字第2012章267号54号楼,69号楼,55号楼5号楼，44号楼，51号楼；济建开预许字第2013
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd34234/#wt_source=phb_04_lp" class="prolink">重汽翡翠东郡</a>
                                    <span class="loc">高新区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>4500</strong>元/平米</p>
                            <p class="up_time">05月03日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=34234" class="my_address">高新区经十路以北 圣井...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd34863/#wt_source=phb_04_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/d3/8d/2/82bac70a0c139f038076bcd5a90_p7_mk7_os51ce24_cm320X240.jpg" title="恒大绿洲">
                                                                                                                    <em class="rankNum">4</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建开预许字第（2011）C0020号 20号楼；济建开预许字第（2011）C0005号 	19号楼；济建开预许字第（2011）C0004号 	18号楼；济建开预许字第（2011）C0007号 	15号楼；济建开预许字第（2011）C0002   10号楼；济建开预许字第（2011）C0012号 	B地块11号楼；济建开预许字第（20
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd34863/#wt_source=phb_04_lp" class="prolink">恒大绿洲</a>
                                    <span class="loc">长清区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>5900</strong>元/平米</p>
                            <p class="up_time">05月04日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=34863" class="my_address">长清大学路与凤凰路交叉...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd34219/#wt_source=phb_04_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/16/38/c/4c12d893a05d7d5578cc94ad5dc_p7_mk7_os5af536_cm320X240.jpg" title="国华东方美郡">
                                                                                                                    <em class="rankNum">5</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2011390号（611）;济建预许2011390号（617）611,615,613,617,612,616,614;济建预许2011483-486号701号楼,704号楼,703号楼,702号楼;济建预许2011389-2011390;607,601,608,605,606,603,609,604,602,610
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd34219/#wt_source=phb_04_lp" class="prolink">国华东方美郡</a>
                                    <span class="loc">市中</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>30000</strong>元/平米</p>
                            <p class="up_time">05月03日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=34219" class="my_address">市中区旅游路28666号，...</a>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                                                <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">本月不可错过</strong>
                                                            <a href="?type=monthly_clicks" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd130788/#wt_source=phb_05_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/7d/c4/0/e20485345196e6cda5f1482d532_p7_mk7_os915739_cm320X240.jpg" title="财富壹号">
                                                                                                                    <em class="rankNumRed">1</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd130788/#wt_source=phb_05_lp" class="prolink">财富壹号</a>
                                    <span class="loc">槐荫</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>8500</strong>元/平米</p>
                            <p class="up_time">05月16日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=130788" class="my_address">济南市槐荫区经十路舜和...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd131858/#wt_source=phb_05_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/02/6f/0/c5f1c4f651f55b2b250cdc9426e_p7_mk7_os84ae07_cm320X240.jpg" title="拉菲公馆">
                                                                                                                    <em class="rankNumRed">2</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>6号楼 济建预许2016028号;5号楼 济建预许2016027号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd131858/#wt_source=phb_05_lp" class="prolink">拉菲公馆</a>
                                    <span class="loc">历下</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>17000</strong>元/平米</p>
                            <p class="up_time">05月04日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=131858" class="my_address">历下区CBD,省博正南转山...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd130727/#wt_source=phb_05_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/fd/47/0/c8543f91dda8f323590f842bd6c_p7_mk7_os840861_cm320X240.jpg" title="林里·天怡">
                                                                                                                    <em class="rankNumRed">3</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建开预许字第（2013）章99号—章129号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd130727/#wt_source=phb_05_lp" class="prolink">林里·天怡</a>
                                    <span class="loc">章丘市</span>
                                </p>
                            </div>
                            <p class="price"><strong>80-130</strong>万元/套</p>
                            <p class="up_time">05月04日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=130727" class="my_address">济南动植物园南邻（与动...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd129458/#wt_source=phb_05_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/34/cb/d/ace9ce28c01be9f781da77d4d32_p7_mk7_os3b1e4c_cm320X240.jpg" title="恒生艾特公寓">
                                                                                                                    <em class="rankNum">4</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015433号 3号楼；济建预许2014012号 2号楼；济建预许2014017号 1号楼
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd129458/#wt_source=phb_05_lp" class="prolink">恒生艾特公寓</a>
                                    <span class="loc">槐荫</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>7000</strong>元/平米</p>
                            <p class="up_time">04月15日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=129458" class="my_address">槐荫无影山中路与济齐路...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd128840/#wt_source=phb_05_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/30/bd/c/54a78fb485de51d45ab3014735b_p7_mk7_os248792_cm320X240.jpg" title="新城·香溢紫郡">
                                                                                                                    <em class="rankNum">5</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2016378号 5号楼；济建预许2016338号 15号楼；济建预许2016221号 9号楼；济建预许2016161号 20号楼；济建预许2016065号 17号楼；济建预许2015719号 21号楼；济建预许2015718号 16号楼；济建预许2015628号 19号楼
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd128840/#wt_source=phb_05_lp" class="prolink">新城·香溢紫郡</a>
                                    <span class="loc">历城</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>6200</strong>元/平米</p>
                            <p class="up_time">05月25日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=128840" class="my_address">工业北路与开源路交叉口...</a>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                                                <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">3个月内入住</strong>
                                                            <a href="?type=reside_3_month" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd126153/#wt_source=phb_06_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/36/5a/0/0d11d25533600735a4ad583bdc7_p7_mk7_os13732d_cm320X240.jpg" title="中国铁建·国际中心">
                                                                                                                    <em class="rankNumRed">1</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015058号，济建预许2015059号，济建预许2015056号，济建预许2015057号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd126153/#wt_source=phb_06_lp" class="prolink">中国铁建·国际中心</a>
                                    <span class="loc">历下</span>
                                </p>
                            </div>
                            <p class="price"><strong>11000-13000</strong>元/平米</p>
                            <p class="up_time">04月07日更新</p>
                                                        <p class="time">入住：2016年06月</p>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd123783/#wt_source=phb_06_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/ce/f1/c/5710925e0b697bd5b8d105681db_p7_mk7_osa37d7d_cm320X240.jpg" title="燕玺台">
                                                                                                                    <em class="rankNumRed">2</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015059号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd123783/#wt_source=phb_06_lp" class="prolink">燕玺台</a>
                                    <span class="loc">历下</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>19000</strong>元/平米</p>
                            <p class="up_time">05月03日更新</p>
                                                        <p class="time">入住：2016年06月</p>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd119076/#wt_source=phb_06_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/d3/52/1/565c351cd17918055a5ef9283a9_p7_mk7_os892a97_cm320X240.jpg" title="佛山静院">
                                                                                                                    <em class="rankNumRed">3</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015082号 6号楼；济建预许2015081号 5号楼；济建预许2015079号 3号楼；济建预许2015078号 2号楼；济建预许2015077号 1号楼
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd119076/#wt_source=phb_06_lp" class="prolink">佛山静院</a>
                                    <span class="loc">历下</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>27000</strong>元/平米</p>
                            <p class="up_time">04月18日更新</p>
                                                        <p class="time">入住：2016年05月</p>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd118087/#wt_source=phb_06_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/67/03/2/d280ecbd752704796f2a6ebbcb8_p7_mk7_osfacbdf_cm320X240.jpg" title="世茂天街">
                                                                                                                    <em class="rankNum">4</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2014369号, 济建预许2014393号 ,济建预许2014368号,济建预许2014401号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd118087/#wt_source=phb_06_lp" class="prolink">世茂天街</a>
                                    <span class="loc">天桥</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>30000</strong>元/平米</p>
                            <p class="up_time">04月26日更新</p>
                                                        <p class="time">入住：2016年06月</p>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd118083/#wt_source=phb_06_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/3e/0d/9/4918676c61178eacdd8655ebb90_p7_mk7_os307a0e_cm320X240.jpg" title="河泰·优山美郡">
                                                                                                                    <em class="rankNum">5</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015104号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd118083/#wt_source=phb_06_lp" class="prolink">河泰·优山美郡</a>
                                    <span class="loc">历城</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>6500</strong>元/平米</p>
                            <p class="up_time">05月03日更新</p>
                                                        <p class="time">入住：2016年07月</p>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                                                <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">精装修</strong>
                                                            <a href="?type=fitment_good" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd124566/#wt_source=phb_07_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/c0/01/b/4a0771e4a85c8ea283bb15223ad_p7_mk7_oscff450_cm320X240.jpg" title="万虹广场">
                                                                                                                    <em class="rankNumRed">1</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd124566/#wt_source=phb_07_lp" class="prolink">万虹广场</a>
                                    <span class="loc">历城</span>
                                </p>
                            </div>
                            <p class="price"><strong>待定</strong></p>
                            <p class="up_time">05月03日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=124566" class="my_address">工业北路与开源路交汇处</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd129702/#wt_source=phb_07_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/23/f2/7/c5e828d58084727b4e7a4e8a4b6_p7_mk7_oscea296_cm320X240.jpg" title="绿城·济南中心">
                                                                                                                    <em class="rankNumRed">2</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2014559号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd129702/#wt_source=phb_07_lp" class="prolink">绿城·济南中心</a>
                                    <span class="loc">历下</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>18000</strong>元/平米</p>
                            <p class="up_time">04月15日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=129702" class="my_address">泉城广场旁，泺源大街商...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd129500/#wt_source=phb_07_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/a7/a8/6/c41c5a01f7a38d559841f09c4e2_p7_mk7_osf1ba81_cm320X240.jpg" title="万科幸福里">
                                                                                                                    <em class="rankNumRed">3</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015086号；济建预许2015160号；济建预许2015159号；济建预许2015049号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd129500/#wt_source=phb_07_lp" class="prolink">万科幸福里</a>
                                    <span class="loc">历城</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>5499</strong>元/平米</p>
                            <p class="up_time">05月03日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=129500" class="my_address">历城区工业南路与飞跃大...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd128283/#wt_source=phb_07_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/af/e5/c/a53f3eeeef058baf27952a474e0_p7_mk7_os639086_cm320X240.jpg" title="济南恒大奥东新都">
                                                                                                                    <em class="rankNum">4</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015666号，济建预许2015666号，济建预许2015665号，济建预许2015665号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd128283/#wt_source=phb_07_lp" class="prolink">济南恒大奥东新都</a>
                                    <span class="loc">历下</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>8600</strong>元/平米</p>
                            <p class="up_time">05月04日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=128283" class="my_address">济南市历下区经十路与凤...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd128014/#wt_source=phb_07_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/3a/ad/0/bc34e723e0ceb8093db3277cd2a_p7_mk7_osb9243c_cm320X240.jpg" title="华润中心">
                                                                                                                    <em class="rankNum">5</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015791号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd128014/#wt_source=phb_07_lp" class="prolink">华润中心</a>
                                    <span class="loc">历下</span>
                                </p>
                            </div>
                            <p class="price"><strong>13000-16000</strong>元/平米</p>
                            <p class="up_time">05月03日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=128014" class="my_address">经十路与姚家东路交汇处...</a>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                                                <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">高性价比</strong>
                                                            <a href="?type=pinpai_list" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd130788/#wt_source=phb_08_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/7d/c4/0/e20485345196e6cda5f1482d532_p7_mk7_os915739_cm320X240.jpg" title="财富壹号">
                                                                                                                    <em class="rankNumRed">1</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd130788/#wt_source=phb_08_lp" class="prolink">财富壹号</a>
                                    <span class="loc">槐荫</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>8500</strong>元/平米</p>
                            <p class="up_time">05月16日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=130788" class="my_address">济南市槐荫区经十路舜和...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd108732/#wt_source=phb_08_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/43/c2/0/b33b2e33ff542d4b645689d4571_p7_mk7_os7bee9b_cm320X240.jpg" title="山东高速广场">
                                                                                                                    <em class="rankNumRed">2</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015797号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd108732/#wt_source=phb_08_lp" class="prolink">山东高速广场</a>
                                    <span class="loc">槐荫</span>
                                </p>
                            </div>
                            <p class="price"><strong>待定</strong></p>
                            <p class="up_time">05月04日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=108732" class="my_address">济南西客站核心区</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd131858/#wt_source=phb_08_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/02/6f/0/c5f1c4f651f55b2b250cdc9426e_p7_mk7_os84ae07_cm320X240.jpg" title="拉菲公馆">
                                                                                                                    <em class="rankNumRed">3</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>6号楼 济建预许2016028号;5号楼 济建预许2016027号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd131858/#wt_source=phb_08_lp" class="prolink">拉菲公馆</a>
                                    <span class="loc">历下</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>17000</strong>元/平米</p>
                            <p class="up_time">05月04日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=131858" class="my_address">历下区CBD,省博正南转山...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd129702/#wt_source=phb_08_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/23/f2/7/c5e828d58084727b4e7a4e8a4b6_p7_mk7_oscea296_cm320X240.jpg" title="绿城·济南中心">
                                                                                                                    <em class="rankNum">4</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2014559号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd129702/#wt_source=phb_08_lp" class="prolink">绿城·济南中心</a>
                                    <span class="loc">历下</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>18000</strong>元/平米</p>
                            <p class="up_time">04月15日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=129702" class="my_address">泉城广场旁，泺源大街商...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd128649/#wt_source=phb_08_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/67/39/0/379d9b9e66b28537312eb661606_p7_mk7_os1a3611_cm320X240.jpg" title="鲁能·领秀公馆">
                                                                                                                    <em class="rankNum">5</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2016141号 37号楼；济建预许2016140号 17号楼；9号楼：济建预许2016011号；4号楼：济建预许2016010号；3号楼：济建预许2016009号；济建预许2016012号 11号楼；济建预许2015709号 42号楼；济建预许2015708号 28号楼；济建预许2015612号 48号楼；济建预许2015612号 47号楼；济建预许2015612号 45号楼；济建预许2015612号 38号楼；济建预许2015611号 29号楼；济建预许2015562号 46号楼；济建预许2015562号 36号楼；济建预许2015561号 34号楼；济建预许2015551号 55号楼、54号楼、53号楼、52号楼、51号楼、50号楼、49号楼；济建预许20
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd128649/#wt_source=phb_08_lp" class="prolink">鲁能·领秀公馆</a>
                                    <span class="loc">市中</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>9400</strong>元/平米</p>
                            <p class="up_time">05月05日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=128649" class="my_address">市中领秀城贵和购物中心...</a>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                                                <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">地铁沿线</strong>
                                                            <a href="?type=nearby_trackline" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd125925/#wt_source=phb_09_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/2e/86/b/cde6ee8a3a82a7e472645b2fb3f_p7_mk7_osccfc82_cm320X240.jpg" title="重汽·翡翠雅郡">
                                                                                                                    <em class="rankNumRed">1</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015514号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd125925/#wt_source=phb_09_lp" class="prolink">重汽·翡翠雅郡</a>
                                    <span class="loc">高新区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>5100</strong>元/平米</p>
                            <p class="up_time">05月03日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=125925" class="my_address">经十东路孙村立交桥北行...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd118382/#wt_source=phb_09_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/8f/e5/a/bee3d7f025188aa66137770a23f_p7_mk7_osaa5b1d_cm320X240.jpg" title="银丰公馆">
                                                                                                                    <em class="rankNumRed">2</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建开预许字第（2014）C012号;济建开预许第（2015）C008号;济建开预许字第（2015）C003号;济建开预许第（2015）C005号;济建开预许第（2015）C028号;济建开预许第（2015）C020号;济建开预许字第（2014）C018号;济建开预许字第（2014）C014号;济建开预许字第（2014）C016号;济建开预许字第（2014）C013号;济建开预许第（2015）C019号;济建开预许字第（2014）C017号;济建开预许第（2015）C021号;济建开预许第（2015）C019号;济建开预许第（2015）C004号;济建开预许第（2015）C021号;济建开预许第（2015）C004号;济建开预许字第（2015）C003
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd118382/#wt_source=phb_09_lp" class="prolink">银丰公馆</a>
                                    <span class="loc">长清区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>5000</strong>元/平米</p>
                            <p class="up_time">05月04日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=118382" class="my_address">长清区大学路与莲台山路...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd118087/#wt_source=phb_09_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/67/03/2/d280ecbd752704796f2a6ebbcb8_p7_mk7_osfacbdf_cm320X240.jpg" title="世茂天街">
                                                                                                                    <em class="rankNumRed">3</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2014369号, 济建预许2014393号 ,济建预许2014368号,济建预许2014401号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd118087/#wt_source=phb_09_lp" class="prolink">世茂天街</a>
                                    <span class="loc">天桥</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>30000</strong>元/平米</p>
                            <p class="up_time">04月26日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=118087" class="my_address">天桥区政府南临</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd115851/#wt_source=phb_09_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/e1/e3/c/82814dc6b702811785b1c1ab3a6_p7_mk7_osf6f2e4_cm320X240.jpg" title="中捷·紫悦华庭">
                                                                                                                    <em class="rankNum">4</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>12号楼，济建预许2015049，11号楼济建预许2015086
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd115851/#wt_source=phb_09_lp" class="prolink">中捷·紫悦华庭</a>
                                    <span class="loc">历城</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>6300</strong>元/平米</p>
                            <p class="up_time">04月26日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=115851" class="my_address">工业南路与飞跃大道交会...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd114288/#wt_source=phb_09_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/35/2e/0/17fb9663547ea8d3c6421b6fea7_p7_mk7_os131eae_cm320X240.jpg" title="济南世茂天城">
                                                                                                                    <em class="rankNum">5</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015702号12号楼；济建预许2015484号6号楼；济建预许2015223号14号楼；济建预许2014463号20号  济建预许2014572号30号楼济建预许2014369号17号楼济建预许2014393号18号楼济建预许2014368号24号楼济建预许2014370号26号楼
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd114288/#wt_source=phb_09_lp" class="prolink">济南世茂天城</a>
                                    <span class="loc">天桥</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>10000</strong>元/平米</p>
                            <p class="up_time">05月19日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=114288" class="my_address">济南天桥区政府南临</a>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                                                <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">教育地产</strong>
                                                            <a href="?type=edu_good" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd119391/#wt_source=phb_10_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/7c/8b/9/ca5ab53d3bd42dd16217b44e62e_p7_mk7_os3042da_cm320X240.jpg" title="淮海·东城御景二期南书房">
                                                                                                                    <em class="rankNumRed">1</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015138号	2#楼，济建预许2015139号6#楼，济建预许2015004号3#楼；济建预许2014641号北区1#楼
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd119391/#wt_source=phb_10_lp" class="prolink">淮海·东城御景二期南书房</a>
                                    <span class="loc">历下</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>7380</strong>元/平米</p>
                            <p class="up_time">05月03日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=119391" class="my_address">历下区花园路与奥体西路...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd117064/#wt_source=phb_10_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/c9/d2/1/4110befaa53c67b8526761a20cf_p7_mk7_ose95d55_cm320X240.jpg" title="原山官邸">
                                                                                                                    <em class="rankNumRed">2</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建开预许字第（2014号）C010号 18号楼,19号楼,20号楼
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd117064/#wt_source=phb_10_lp" class="prolink">原山官邸</a>
                                    <span class="loc">长清区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>4700</strong>元/平米</p>
                            <p class="up_time">03月09日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=117064" class="my_address">济南市长清区峰山路南段...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd117058/#wt_source=phb_10_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/0c/ef/4/af1d915a75991be822e723e0820_p7_mk7_os476971_cm320X240.jpg" title="德润天玺">
                                                                                                                    <em class="rankNumRed">3</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015171号	5#楼济建预许2014687 	B1地块4号楼 济建预许2014688 	B1地块7号楼
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd117058/#wt_source=phb_10_lp" class="prolink">德润天玺</a>
                                    <span class="loc">高新区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>8800</strong>元/平米</p>
                            <p class="up_time">05月04日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=117058" class="my_address">济南奥体中心东行1500米...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd116994/#wt_source=phb_10_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/75/16/2/27fc5f219d591e91e37a27d270f_p7_mk7_os9ff58b_cm320X240.jpg" title="恒大天玺">
                                                                                                                    <em class="rankNum">4</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015029号2#，济建预许2014478号6#，济建预许2014336号5#，济建预许2014335号4#，济建预许2014334号3#
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd116994/#wt_source=phb_10_lp" class="prolink">恒大天玺</a>
                                    <span class="loc">槐荫</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>9800</strong>元/平米</p>
                            <p class="up_time">05月04日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=116994" class="my_address">济南市槐荫区兴福寺与淄...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd116656/#wt_source=phb_10_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/6b/9f/f/937867502bd56e8c476313fcc7b_p7_mk7_osaab388_cm320X240.jpg" title="中海铂宫央墅">
                                                                                                                    <em class="rankNum">5</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2014540号 	B-2地块 济建预许2013082号 	中海国际社区项目A-4地块100
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd116656/#wt_source=phb_10_lp" class="prolink">中海铂宫央墅</a>
                                    <span class="loc">市中</span>
                                </p>
                            </div>
                            <p class="price">总价约<strong>350</strong>万元/套</p>
                            <p class="up_time">04月26日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=116656" class="my_address">二环南路与阳光新路交汇...</a>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                                                <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">区域列表</strong>
                                                            <a href="?type=region_list" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd130660/#wt_source=phb_11_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/1f/58/c/9ed4c245c563a263c475775b6fa_p7_mk7_os05d2ce_cm320X240.jpg" title="海口恒大·美丽沙">
                                                                                                                    <em class="rankNumRed">1</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>海房预字（2015）0039号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd130660/#wt_source=phb_11_lp" class="prolink">海口恒大·美丽沙</a>
                                    <span class="loc">海口市</span>
                                </p>
                            </div>
                            <p class="price">总价约<strong>80</strong>万元/套</p>
                            <p class="up_time">05月04日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=130660" class="my_address">海口海甸岛碧海大道29号</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd111720/#wt_source=phb_11_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/8e/89/b/7beeb20188b720bc3c1707e33d8_p7_mk7_os6027e3_cm320X240.jpg" title="中国济南泺口皮革城">
                                                                                                                    <em class="rankNumRed">2</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd111720/#wt_source=phb_11_lp" class="prolink">中国济南泺口皮革城</a>
                                    <span class="loc">天桥</span>
                                </p>
                            </div>
                            <p class="price"><strong>待定</strong></p>
                            <p class="up_time">05月03日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=111720" class="my_address">山东省济南市天桥区小清...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd109138/#wt_source=phb_11_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/82/8b/2/6f9011a3aeccb0106dffca9e18d_p7_mk7_os1db7b5_cm320X240.jpg" title="清河上城">
                                                                                                                    <em class="rankNumRed">3</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd109138/#wt_source=phb_11_lp" class="prolink">清河上城</a>
                                    <span class="loc">新泰</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>3500</strong>元/平米</p>
                            <p class="up_time">09月10日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=109138" class="my_address">东平县滨河大道北侧，清...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd84191/#wt_source=phb_11_lp" class="imglink" >
                                    <img src="http://cache.house.sina.com.cn/datahouse/99/76/9749515ab5dae6dea1bd585c1cccb069_320X240.jpg" title="淄博华润·中央公园">
                                                                                                                    <em class="rankNum">4</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd84191/#wt_source=phb_11_lp" class="prolink">淄博华润·中央公园</a>
                                    <span class="loc">淄博市</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>6500</strong>元/平米</p>
                            <p class="up_time">11月24日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=84191" class="my_address">张店人民西路1号（人民...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd51807/#wt_source=phb_11_lp" class="imglink" >
                                    <img src="http://data.house.sina.com.cn/images/default_m.jpg" title="泉景·恒展商务大厦">
                                                                                                                    <em class="rankNum">5</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd51807/#wt_source=phb_11_lp" class="prolink">泉景·恒展商务大厦</a>
                                    <span class="loc">历下</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>7800</strong>元/平米</p>
                            <p class="up_time">03月25日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=51807" class="my_address">花园路与历山路交汇处</a>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                                                <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">拼音列表</strong>
                                                            <a href="?type=pinyin_list" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd130332/#wt_source=phb_12_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/8a/ba/7/fb9593f53ef604bcce49bc6f485_p7_mk7_os0fb3a8_cm320X240.jpg" title="缤润汇">
                                                                                                                    <em class="rankNumRed">B</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd130332/#wt_source=phb_12_lp" class="prolink">缤润汇</a>
                                    <span class="loc">高新区</span>
                                </p>
                            </div>
                            <p class="price"><strong>待定</strong></p>
                            <p class="up_time">04月15日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=130332" class="my_address">凤凰路与旅游路交汇处</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd130788/#wt_source=phb_12_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/7d/c4/0/e20485345196e6cda5f1482d532_p7_mk7_os915739_cm320X240.jpg" title="财富壹号">
                                                                                                                    <em class="rankNumRed">C</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd130788/#wt_source=phb_12_lp" class="prolink">财富壹号</a>
                                    <span class="loc">槐荫</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>8500</strong>元/平米</p>
                            <p class="up_time">05月16日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=130788" class="my_address">济南市槐荫区经十路舜和...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd128203/#wt_source=phb_12_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/70/07/1/2793b10114453711b7425ed1a4c_p7_mk7_os7117a2_cm320X240.jpg" title="东8区·企业公馆">
                                                                                                                    <em class="rankNumRed">D</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd128203/#wt_source=phb_12_lp" class="prolink">东8区·企业公馆</a>
                                    <span class="loc">历城</span>
                                </p>
                            </div>
                            <p class="price"><strong>待定</strong></p>
                            <p class="up_time">04月18日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=128203" class="my_address">济南市历城区世纪大道和...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd131824/#wt_source=phb_12_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/f6/83/d/48cb828a15d960e5fc144d60c1c_p7_mk7_osa93282_cm320X240.jpg" title="凤凰国际">
                                                                                                                    <em class="rankNum">F</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许：2015720；济建预许：2015721；济建预许：2016013；济建预许：2106014；济建预许：2016015
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd131824/#wt_source=phb_12_lp" class="prolink">凤凰国际</a>
                                    <span class="loc">高新区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>8700</strong>元/平米</p>
                            <p class="up_time">05月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=131824" class="my_address">旅游北路与凤凰路交汇处...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd130017/#wt_source=phb_12_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/c9/a6/4/5630ed8e53bd6100bb54a6e1934_p7_mk7_os2b1dd6_cm320X240.jpg" title="高新绿城·玉蘭花园">
                                                                                                                    <em class="rankNum">G</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015796号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd130017/#wt_source=phb_12_lp" class="prolink">高新绿城·玉蘭花园</a>
                                    <span class="loc">高新区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>10000</strong>元/平米</p>
                            <p class="up_time">05月04日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=130017" class="my_address">舜华南路与旅游路路口向...</a>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                                                <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">一居</strong>
                                                            <a href="?type=rtype1" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd129702/#wt_source=phb_13_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/23/f2/7/c5e828d58084727b4e7a4e8a4b6_p7_mk7_oscea296_cm320X240.jpg" title="绿城·济南中心">
                                                                                                                    <em class="rankNumRed">1</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2014559号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd129702/#wt_source=phb_13_lp" class="prolink">绿城·济南中心</a>
                                    <span class="loc">历下</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>18000</strong>元/平米</p>
                            <p class="up_time">04月15日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=129702" class="my_address">泉城广场旁，泺源大街商...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd129458/#wt_source=phb_13_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/34/cb/d/ace9ce28c01be9f781da77d4d32_p7_mk7_os3b1e4c_cm320X240.jpg" title="恒生艾特公寓">
                                                                                                                    <em class="rankNumRed">2</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015433号 3号楼；济建预许2014012号 2号楼；济建预许2014017号 1号楼
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd129458/#wt_source=phb_13_lp" class="prolink">恒生艾特公寓</a>
                                    <span class="loc">槐荫</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>7000</strong>元/平米</p>
                            <p class="up_time">04月15日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=129458" class="my_address">槐荫无影山中路与济齐路...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd129149/#wt_source=phb_13_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/15/99/1/d34b0cc2842e7767123156f5279_p7_mk7_os0ed937_cm320X240.jpg" title="绿地·海珀天沅">
                                                                                                                    <em class="rankNumRed">3</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015637号，济建预许2015636号，济建预许2015634号，济建预许2015635号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd129149/#wt_source=phb_13_lp" class="prolink">绿地·海珀天沅</a>
                                    <span class="loc">市中</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>14000</strong>元/平米</p>
                            <p class="up_time">05月03日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=129149" class="my_address">市中区郎茂山路西侧、省...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd128230/#wt_source=phb_13_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/0f/29/2/9091f207b171faa99d5a7b9fb83_p7_mk7_os3de749_cm320X240.jpg" title="祥泰·和院">
                                                                                                                    <em class="rankNum">4</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015589号，济建预许2015588号，济建预许2015572号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd128230/#wt_source=phb_13_lp" class="prolink">祥泰·和院</a>
                                    <span class="loc">历下</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>16000</strong>元/平米</p>
                            <p class="up_time">04月15日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=128230" class="my_address">和平路与燕子山小区东路...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd125925/#wt_source=phb_13_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/2e/86/b/cde6ee8a3a82a7e472645b2fb3f_p7_mk7_osccfc82_cm320X240.jpg" title="重汽·翡翠雅郡">
                                                                                                                    <em class="rankNum">5</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015514号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd125925/#wt_source=phb_13_lp" class="prolink">重汽·翡翠雅郡</a>
                                    <span class="loc">高新区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>5100</strong>元/平米</p>
                            <p class="up_time">05月03日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=125925" class="my_address">经十东路孙村立交桥北行...</a>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                                                <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">两居</strong>
                                                            <a href="?type=rtype2" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd130727/#wt_source=phb_14_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/fd/47/0/c8543f91dda8f323590f842bd6c_p7_mk7_os840861_cm320X240.jpg" title="林里·天怡">
                                                                                                                    <em class="rankNumRed">1</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建开预许字第（2013）章99号—章129号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd130727/#wt_source=phb_14_lp" class="prolink">林里·天怡</a>
                                    <span class="loc">章丘市</span>
                                </p>
                            </div>
                            <p class="price"><strong>80-130</strong>万元/套</p>
                            <p class="up_time">05月04日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=130727" class="my_address">济南动植物园南邻（与动...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd129880/#wt_source=phb_14_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/75/ed/5/0a2327fc8b6cf2488033aa89e75_p7_mk7_osa87ebc_cm320X240.jpg" title="荣盛·花语馨苑">
                                                                                                                    <em class="rankNumRed">2</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2016117号 4号楼；济建预许2016099号 2号楼；济建预许2016098号 1号楼
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd129880/#wt_source=phb_14_lp" class="prolink">荣盛·花语馨苑</a>
                                    <span class="loc">天桥</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>7000</strong>元/平米</p>
                            <p class="up_time">05月25日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=129880" class="my_address">天桥区无影山北路3号</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd129500/#wt_source=phb_14_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/a7/a8/6/c41c5a01f7a38d559841f09c4e2_p7_mk7_osf1ba81_cm320X240.jpg" title="万科幸福里">
                                                                                                                    <em class="rankNumRed">3</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015086号；济建预许2015160号；济建预许2015159号；济建预许2015049号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd129500/#wt_source=phb_14_lp" class="prolink">万科幸福里</a>
                                    <span class="loc">历城</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>5499</strong>元/平米</p>
                            <p class="up_time">05月03日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=129500" class="my_address">历城区工业南路与飞跃大...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd129392/#wt_source=phb_14_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/10/64/d/1aa0e34f07ae4025116ff61937e_p7_mk7_os034e33_cm320X240.jpg" title="绿地·国际城">
                                                                                                                    <em class="rankNum">4</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd129392/#wt_source=phb_14_lp" class="prolink">绿地·国际城</a>
                                    <span class="loc">市中</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>7000</strong>元/平米</p>
                            <p class="up_time">05月09日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=129392" class="my_address">新二环南路北侧，济微公...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd128605/#wt_source=phb_14_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/65/68/f/d94b0517eacfdb2f9645296ae61_p7_mk7_osbda21e_cm320X240.jpg" title="山钢·新天地">
                                                                                                                    <em class="rankNum">5</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2016138号 4号楼；济建预许2016137号 2号楼；济建预许2015741号 1号楼；济建预许2015742号 6号楼；济建预许2015541号 7#楼；济建预许2015540号 5#楼
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd128605/#wt_source=phb_14_lp" class="prolink">山钢·新天地</a>
                                    <span class="loc">高新区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>12000</strong>元/平米</p>
                            <p class="up_time">05月25日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=128605" class="my_address">济南市工业南路和奥体中...</a>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                                                            <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">5千元以内</strong>
                                        <a href="?type=pricerange&type_value=988" class="btnmore">更多 &gt;</a>
                </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd118382/#wt_source=phb_15_lp" class="imglink">
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/8f/e5/a/bee3d7f025188aa66137770a23f_p7_mk7_osaa5b1d_cm320X240.jpg" title="银丰公馆">
                                                                        <em class="rankNumRed">1</em>
                                                                        <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建开预许字第（2014）C012号;济建开预许第（2015）C008号;济建开预许字第（2015）C003号;济建开预许第（2015）C005号;济建开预许第（2015）C028号;济建开预许第（2015）C020号;济建开预许字第（2014）C018号;济建开预许字第（2014）C014号;济建开预许字第（2014）C016号;济建开预许字第（2014）C013号;济建开预许第（2015）C019号;济建开预许字第（2014）C017号;济建开预许第（2015）C021号;济建开预许第（2015）C019号;济建开预许第（2015）C004号;济建开预许第（2015）C021号;济建开预许第（2015）C004号;济建开预许字第（2015）C003
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd118382/#wt_source=phb_15_lp" class="prolink">银丰公馆</a>
                                    <span class="loc">长清区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>5000</strong>元/平米</p>
                            <p class="up_time">05月04日更新</p>
                            <p class="time" title="长清区大学路与莲台山路交汇处东北侧">
                                <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=118382" class="my_address">长清区大学路与莲台山路...</a>
                            </p>
                        </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd117974/#wt_source=phb_15_lp" class="imglink">
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/53/7a/9/3e763a753f24df9464e31af765a_p7_mk7_os36be7e_cm320X240.jpg" title="盛景城">
                                                                        <em class="rankNumRed">2</em>
                                                                        <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济商房开预许字第201523号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd117974/#wt_source=phb_15_lp" class="prolink">盛景城</a>
                                    <span class="loc">商河县</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>3500</strong>元/平米</p>
                            <p class="up_time">05月09日更新</p>
                            <p class="time" title="商河汽车站北100米">
                                <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=117974" class="my_address">商河汽车站北100米</a>
                            </p>
                        </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd117064/#wt_source=phb_15_lp" class="imglink">
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/c9/d2/1/4110befaa53c67b8526761a20cf_p7_mk7_ose95d55_cm320X240.jpg" title="原山官邸">
                                                                        <em class="rankNumRed">3</em>
                                                                        <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建开预许字第（2014号）C010号 18号楼,19号楼,20号楼
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd117064/#wt_source=phb_15_lp" class="prolink">原山官邸</a>
                                    <span class="loc">长清区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>4700</strong>元/平米</p>
                            <p class="up_time">03月09日更新</p>
                            <p class="time" title="济南市长清区峰山路南段长清中学南800米">
                                <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=117064" class="my_address">济南市长清区峰山路南段...</a>
                            </p>
                        </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd111960/#wt_source=phb_15_lp" class="imglink">
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/f3/23/1/cb7cd343a2a0af85af7960f45b6_p7_mk7_os313bda_cm320X240.jpg" title="卓亚·香格里">
                                                                        <em class="rankNum">4</em>
                                                                        <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建开预许字第（平）2014-027号，济建开预许字第（平）2014-028号，济建开预许字第（平）2014-029号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd111960/#wt_source=phb_15_lp" class="prolink">卓亚·香格里</a>
                                    <span class="loc">平阴县</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>4000</strong>元/平米</p>
                            <p class="up_time">05月09日更新</p>
                            <p class="time" title="济南市平阴县锦东新区">
                                <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=111960" class="my_address">济南市平阴县锦东新区</a>
                            </p>
                        </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd110446/#wt_source=phb_15_lp" class="imglink">
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/b2/89/c/30bac29db00754372313cb28750_p7_mk7_os64b9ad_cm320X240.jpg" title="鑫茂·齐鲁科技城">
                                                                        <em class="rankNum">5</em>
                                                                        <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2013532号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd110446/#wt_source=phb_15_lp" class="prolink">鑫茂·齐鲁科技城</a>
                                    <span class="loc">天桥</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>3860</strong>元/平米</p>
                            <p class="up_time">05月09日更新</p>
                            <p class="time" title="天桥区308国道北梓东大道1号">
                                <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=110446" class="my_address">天桥区308国道北梓东大...</a>
                            </p>
                        </li>
                                            </ul>
                </div>
            </div>
                                                <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">5千-6千元</strong>
                                        <a href="?type=pricerange&type_value=989" class="btnmore">更多 &gt;</a>
                </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd127604/#wt_source=phb_16_lp" class="imglink">
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/f8/93/0/5f74faf23a22ce38a2153d89f68_p7_mk7_osfba1fc_cm320X240.jpg" title="新奇世界国际度假区济南鹊山">
                                                                        <em class="rankNumRed">1</em>
                                                                        <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015462号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd127604/#wt_source=phb_16_lp" class="prolink">新奇世界国际度假区济南鹊山</a>
                                    <span class="loc">天桥</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>6000</strong>元/平米</p>
                            <p class="up_time">05月03日更新</p>
                            <p class="time" title="天桥二环西路北延建邦收费站北200米">
                                <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=127604" class="my_address">天桥二环西路北延建邦收...</a>
                            </p>
                        </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd125925/#wt_source=phb_16_lp" class="imglink">
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/2e/86/b/cde6ee8a3a82a7e472645b2fb3f_p7_mk7_osccfc82_cm320X240.jpg" title="重汽·翡翠雅郡">
                                                                        <em class="rankNumRed">2</em>
                                                                        <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015514号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd125925/#wt_source=phb_16_lp" class="prolink">重汽·翡翠雅郡</a>
                                    <span class="loc">高新区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>5100</strong>元/平米</p>
                            <p class="up_time">05月03日更新</p>
                            <p class="time" title="经十东路孙村立交桥北行800米（彩虹湖公园对面）">
                                <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=125925" class="my_address">经十东路孙村立交桥北行...</a>
                            </p>
                        </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd123643/#wt_source=phb_16_lp" class="imglink">
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/9a/10/8/8a69878db8c1f91b0de31e55b52_p7_mk7_os0253e5_cm320X240.jpg" title="融汇城">
                                                                        <em class="rankNumRed">3</em>
                                                                        <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015586号，济建预许2015167号，济建预许2015166号，济建预许2015587号，济建预许2015275号，济建预许2015115号，济建预许2015165号，济建预许2015432号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd123643/#wt_source=phb_16_lp" class="prolink">融汇城</a>
                                    <span class="loc">市中</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>6000</strong>元/平米</p>
                            <p class="up_time">05月04日更新</p>
                            <p class="time" title="二环南路与二环西路交汇处">
                                <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=123643" class="my_address">二环南路与二环西路交汇...</a>
                            </p>
                        </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd121216/#wt_source=phb_16_lp" class="imglink">
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/9e/04/9/c456cddfd61fb2db1eadcf6104e_p7_mk7_os65e4de_cm320X240.jpg" title="绿地城">
                                                                        <em class="rankNum">4</em>
                                                                        <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2016008号,济建预许2016007号,济建预许2016006号,济建预许2016005号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd121216/#wt_source=phb_16_lp" class="prolink">绿地城</a>
                                    <span class="loc">历城</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>6000</strong>元/平米</p>
                            <p class="up_time">05月04日更新</p>
                            <p class="time" title="历城区体育中心对面">
                                <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=121216" class="my_address">历城区体育中心对面</a>
                            </p>
                        </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd121147/#wt_source=phb_16_lp" class="imglink">
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/a2/3f/4/09df0ddca4bc8a47dca1d1d3904_p7_mk7_osc3dc26_cm320X240.jpg" title="黄河古镇">
                                                                        <em class="rankNum">5</em>
                                                                        <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济阳房预许字第（2014）130号，济阳房预许字第（2014）129号，济阳房预许字第（2014）128号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd121147/#wt_source=phb_16_lp" class="prolink">黄河古镇</a>
                                    <span class="loc">济阳县</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>6000</strong>元/平米</p>
                            <p class="up_time">05月09日更新</p>
                            <p class="time" title="济阳县新元大街与经六路交汇处">
                                <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=121147" class="my_address">济阳县新元大街与经六路...</a>
                            </p>
                        </li>
                                            </ul>
                </div>
            </div>
                                                <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">6千-7千元</strong>
                                        <a href="?type=pricerange&type_value=990" class="btnmore">更多 &gt;</a>
                </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd129880/#wt_source=phb_17_lp" class="imglink">
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/75/ed/5/0a2327fc8b6cf2488033aa89e75_p7_mk7_osa87ebc_cm320X240.jpg" title="荣盛·花语馨苑">
                                                                        <em class="rankNumRed">1</em>
                                                                        <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2016117号 4号楼；济建预许2016099号 2号楼；济建预许2016098号 1号楼
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd129880/#wt_source=phb_17_lp" class="prolink">荣盛·花语馨苑</a>
                                    <span class="loc">天桥</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>7000</strong>元/平米</p>
                            <p class="up_time">05月25日更新</p>
                            <p class="time" title="天桥区无影山北路3号">
                                <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=129880" class="my_address">天桥区无影山北路3号</a>
                            </p>
                        </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd129458/#wt_source=phb_17_lp" class="imglink">
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/34/cb/d/ace9ce28c01be9f781da77d4d32_p7_mk7_os3b1e4c_cm320X240.jpg" title="恒生艾特公寓">
                                                                        <em class="rankNumRed">2</em>
                                                                        <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015433号 3号楼；济建预许2014012号 2号楼；济建预许2014017号 1号楼
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd129458/#wt_source=phb_17_lp" class="prolink">恒生艾特公寓</a>
                                    <span class="loc">槐荫</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>7000</strong>元/平米</p>
                            <p class="up_time">04月15日更新</p>
                            <p class="time" title="槐荫无影山中路与济齐路交汇处（重汽彩世界西邻）">
                                <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=129458" class="my_address">槐荫无影山中路与济齐路...</a>
                            </p>
                        </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd128840/#wt_source=phb_17_lp" class="imglink">
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/30/bd/c/54a78fb485de51d45ab3014735b_p7_mk7_os248792_cm320X240.jpg" title="新城·香溢紫郡">
                                                                        <em class="rankNumRed">3</em>
                                                                        <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2016378号 5号楼；济建预许2016338号 15号楼；济建预许2016221号 9号楼；济建预许2016161号 20号楼；济建预许2016065号 17号楼；济建预许2015719号 21号楼；济建预许2015718号 16号楼；济建预许2015628号 19号楼
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd128840/#wt_source=phb_17_lp" class="prolink">新城·香溢紫郡</a>
                                    <span class="loc">历城</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>6200</strong>元/平米</p>
                            <p class="up_time">05月25日更新</p>
                            <p class="time" title="工业北路与开源路交叉口北600米路东">
                                <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=128840" class="my_address">工业北路与开源路交叉口...</a>
                            </p>
                        </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd121783/#wt_source=phb_17_lp" class="imglink">
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/b5/81/1/82c5caabd9c9b517ee740bef9ea_p7_mk7_os33dc9f_cm320X240.jpg" title="中建新悦城">
                                                                        <em class="rankNum">4</em>
                                                                        <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2016189号 二期11号楼，济建预许2016031号 14号楼；济建预许2014633号 1号楼，济建预许2015210号 4号楼，济建预许2014634号 3号楼
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd121783/#wt_source=phb_17_lp" class="prolink">中建新悦城</a>
                                    <span class="loc">历城</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>6400</strong>元/平米</p>
                            <p class="up_time">04月18日更新</p>
                            <p class="time" title="历城区飞跃大道与凤歧路交汇处">
                                <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=121783" class="my_address">历城区飞跃大道与凤歧路...</a>
                            </p>
                        </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd118653/#wt_source=phb_17_lp" class="imglink">
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/07/57/8/0e5fbdb0553c484275ca5efb50c_p7_mk7_os47a648_cm320X240.jpg" title="中海·华山珑城">
                                                                        <em class="rankNum">5</em>
                                                                        <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015320号，济建预许2014092号，济建预许2014091号，济建预许2014090号，济建预许2014466号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd118653/#wt_source=phb_17_lp" class="prolink">中海·华山珑城</a>
                                    <span class="loc">历城</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>7000</strong>元/平米</p>
                            <p class="up_time">04月05日更新</p>
                            <p class="time" title="位于小清河北路和二环东路交汇处东北部（北临济青高速，西至二环东路，南至小清河）">
                                <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=118653" class="my_address">位于小清河北路和二环东...</a>
                            </p>
                        </li>
                                            </ul>
                </div>
            </div>
                                                <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">7千-9千元</strong>
                                        <a href="?type=pricerange&type_value=991" class="btnmore">更多 &gt;</a>
                </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd130788/#wt_source=phb_18_lp" class="imglink">
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/7d/c4/0/e20485345196e6cda5f1482d532_p7_mk7_os915739_cm320X240.jpg" title="财富壹号">
                                                                        <em class="rankNumRed">1</em>
                                                                        <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd130788/#wt_source=phb_18_lp" class="prolink">财富壹号</a>
                                    <span class="loc">槐荫</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>8500</strong>元/平米</p>
                            <p class="up_time">05月16日更新</p>
                            <p class="time" title="济南市槐荫区经十路舜和酒店西临">
                                <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=130788" class="my_address">济南市槐荫区经十路舜和...</a>
                            </p>
                        </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd128283/#wt_source=phb_18_lp" class="imglink">
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/af/e5/c/a53f3eeeef058baf27952a474e0_p7_mk7_os639086_cm320X240.jpg" title="济南恒大奥东新都">
                                                                        <em class="rankNumRed">2</em>
                                                                        <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015666号，济建预许2015666号，济建预许2015665号，济建预许2015665号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd128283/#wt_source=phb_18_lp" class="prolink">济南恒大奥东新都</a>
                                    <span class="loc">历下</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>8600</strong>元/平米</p>
                            <p class="up_time">05月04日更新</p>
                            <p class="time" title="济南市历下区经十路与凤山路交叉口向北800米路西">
                                <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=128283" class="my_address">济南市历下区经十路与凤...</a>
                            </p>
                        </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd128145/#wt_source=phb_18_lp" class="imglink">
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/9f/b7/5/ec54cb72896ffe9fa7b3b1c63cd_p7_mk7_os44958b_cm320X240.jpg" title="中建长清湖·瑜园">
                                                                        <em class="rankNumRed">3</em>
                                                                        <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2014544
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd128145/#wt_source=phb_18_lp" class="prolink">中建长清湖·瑜园</a>
                                    <span class="loc">长清区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>8000</strong>元/平米</p>
                            <p class="up_time">05月04日更新</p>
                            <p class="time" title="长清区 大学科技园区，芙蓉路与海棠路交汇处">
                                <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=128145" class="my_address">长清区 大学科技园区，...</a>
                            </p>
                        </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd127557/#wt_source=phb_18_lp" class="imglink">
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/63/87/a/01ec31d6b956f8fef0ac768feba_p7_mk7_os8264bb_cm320X240.jpg" title="万科金色悦城">
                                                                        <em class="rankNum">4</em>
                                                                        <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015533号，济建预许2015532号，济建预许2015531号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd127557/#wt_source=phb_18_lp" class="prolink">万科金色悦城</a>
                                    <span class="loc">天桥</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>7200</strong>元/平米</p>
                            <p class="up_time">05月03日更新</p>
                            <p class="time" title="济南市天桥区二环北路与无影山北路交汇处路北">
                                <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=127557" class="my_address">济南市天桥区二环北路与...</a>
                            </p>
                        </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd127246/#wt_source=phb_18_lp" class="imglink">
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/26/7d/d/b106e62be9875cd90979e5a045e_p7_mk7_os030fca_cm320X240.jpg" title="景和山庄">
                                                                        <em class="rankNum">5</em>
                                                                        <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015279号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd127246/#wt_source=phb_18_lp" class="prolink">景和山庄</a>
                                    <span class="loc">历城</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>8800</strong>元/平米</p>
                            <p class="up_time">05月04日更新</p>
                            <p class="time" title="历城区经十东路与凤鸣路交界处山东建筑大学东邻">
                                <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=127246" class="my_address">历城区经十东路与凤鸣路...</a>
                            </p>
                        </li>
                                            </ul>
                </div>
            </div>
                                                                            <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">月供3000元以内</strong>
                                                            <a href="?type=month_return_3k" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd129880/#wt_source=phb_19_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/75/ed/5/0a2327fc8b6cf2488033aa89e75_p7_mk7_osa87ebc_cm320X240.jpg" title="荣盛·花语馨苑">
                                                                                                                    <em class="rankNumRed">1</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2016117号 4号楼；济建预许2016099号 2号楼；济建预许2016098号 1号楼
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd129880/#wt_source=phb_19_lp" class="prolink">荣盛·花语馨苑</a>
                                    <span class="loc">天桥</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>7000</strong>元/平米</p>
                            <p class="up_time">05月25日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=129880" class="my_address">天桥区无影山北路3号</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd129458/#wt_source=phb_19_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/34/cb/d/ace9ce28c01be9f781da77d4d32_p7_mk7_os3b1e4c_cm320X240.jpg" title="恒生艾特公寓">
                                                                                                                    <em class="rankNumRed">2</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015433号 3号楼；济建预许2014012号 2号楼；济建预许2014017号 1号楼
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd129458/#wt_source=phb_19_lp" class="prolink">恒生艾特公寓</a>
                                    <span class="loc">槐荫</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>7000</strong>元/平米</p>
                            <p class="up_time">04月15日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=129458" class="my_address">槐荫无影山中路与济齐路...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd128840/#wt_source=phb_19_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/30/bd/c/54a78fb485de51d45ab3014735b_p7_mk7_os248792_cm320X240.jpg" title="新城·香溢紫郡">
                                                                                                                    <em class="rankNumRed">3</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2016378号 5号楼；济建预许2016338号 15号楼；济建预许2016221号 9号楼；济建预许2016161号 20号楼；济建预许2016065号 17号楼；济建预许2015719号 21号楼；济建预许2015718号 16号楼；济建预许2015628号 19号楼
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd128840/#wt_source=phb_19_lp" class="prolink">新城·香溢紫郡</a>
                                    <span class="loc">历城</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>6200</strong>元/平米</p>
                            <p class="up_time">05月25日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=128840" class="my_address">工业北路与开源路交叉口...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd128680/#wt_source=phb_19_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/ab/2b/7/6bad6852a74275674ad5c8eb65f_p7_mk7_osb5c90b_cm320X240.jpg" title="汇隆广场">
                                                                                                                    <em class="rankNum">4</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd128680/#wt_source=phb_19_lp" class="prolink">汇隆广场</a>
                                    <span class="loc">历下</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>10000</strong>元/平米</p>
                            <p class="up_time">04月15日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=128680" class="my_address">华能路38号</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/sd128283/#wt_source=phb_19_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/af/e5/c/a53f3eeeef058baf27952a474e0_p7_mk7_os639086_cm320X240.jpg" title="济南恒大奥东新都">
                                                                                                                    <em class="rankNum">5</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>济建预许2015666号，济建预许2015666号，济建预许2015665号，济建预许2015665号
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/sd128283/#wt_source=phb_19_lp" class="prolink">济南恒大奥东新都</a>
                                    <span class="loc">历下</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>8600</strong>元/平米</p>
                            <p class="up_time">05月04日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=128283" class="my_address">济南市历下区经十路与凤...</a>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                                                <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">二手房小区</strong>
                                        <span class="titSmall"><em class="xred">TOP 100</em></span>
                                                            <a href="/sd/esf/" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="http://sd.esf.sina.com.cn/info/678?bi=tg&type=house-pc&pos=data-esf#wt_source=phb_20_lp" class="imglink" >
                                    <img src="http://i3.esfimg.com/imp/51931de02f458293ff3402db1e7edfd3_s155X115_os4a34a7.jpg" title="中海国际社区">
                                                                                                                    <em class="rankNumRed">1</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="http://sd.esf.sina.com.cn/info/678?bi=tg&type=house-pc&pos=data-esf#wt_source=phb_20_lp" class="prolink">中海国际社区</a>
                                    <span class="loc">市中</span>
                                </p>
                            </div>
                            <p class="price"></p>
                            <p class="up_time">更新</p>
                                                        <a target="_blank" href="http://sd.esf.sina.com.cn/map/?q=%E4%B8%AD%E6%B5%B7%E5%9B%BD%E9%99%85%E7%A4%BE%E5%8C%BA&bi=tg&type=house-pc&pos=data-esf" class="my_address">市中区九曲片区</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="http://sd.esf.sina.com.cn/info/662?bi=tg&type=house-pc&pos=data-esf#wt_source=phb_20_lp" class="imglink" >
                                    <img src="http://i5.esfimg.com/imp/51931e870e4586b65de10f452de7d968_s155X115_os276e55.jpg" title="鲁能领秀城">
                                                                                                                    <em class="rankNumRed">2</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="http://sd.esf.sina.com.cn/info/662?bi=tg&type=house-pc&pos=data-esf#wt_source=phb_20_lp" class="prolink">鲁能领秀城</a>
                                    <span class="loc">市中</span>
                                </p>
                            </div>
                            <p class="price"></p>
                            <p class="up_time">更新</p>
                                                        <a target="_blank" href="http://sd.esf.sina.com.cn/map/?q=%E9%B2%81%E8%83%BD%E9%A2%86%E7%A7%80%E5%9F%8E&bi=tg&type=house-pc&pos=data-esf" class="my_address">市中区舜耕路延长线</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="http://sd.esf.sina.com.cn/info/831?bi=tg&type=house-pc&pos=data-esf#wt_source=phb_20_lp" class="imglink" >
                                    <img src="http://i3.esfimg.com/imp/51931b9860855406fe8ed354d4670193_s155X115_osad9cd5.jpg" title="重汽翡翠郡">
                                                                                                                    <em class="rankNumRed">3</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="http://sd.esf.sina.com.cn/info/831?bi=tg&type=house-pc&pos=data-esf#wt_source=phb_20_lp" class="prolink">重汽翡翠郡</a>
                                    <span class="loc">天桥</span>
                                </p>
                            </div>
                            <p class="price"></p>
                            <p class="up_time">更新</p>
                                                        <a target="_blank" href="http://sd.esf.sina.com.cn/map/?q=%E9%87%8D%E6%B1%BD%E7%BF%A1%E7%BF%A0%E9%83%A1&bi=tg&type=house-pc&pos=data-esf" class="my_address">济南市西工商河路13号</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="http://sd.esf.sina.com.cn/info/430?bi=tg&type=house-pc&pos=data-esf#wt_source=phb_20_lp" class="imglink" >
                                    <img src="http://i6.esfimg.com/imp/51931b92ba85918c6b56349d91f82000_s155X115_osef961d.jpg" title="名士豪庭">
                                                                                                                    <em class="rankNum">4</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="http://sd.esf.sina.com.cn/info/430?bi=tg&type=house-pc&pos=data-esf#wt_source=phb_20_lp" class="prolink">名士豪庭</a>
                                    <span class="loc">历下</span>
                                </p>
                            </div>
                            <p class="price"></p>
                            <p class="up_time">更新</p>
                                                        <a target="_blank" href="http://sd.esf.sina.com.cn/map/?q=%E5%90%8D%E5%A3%AB%E8%B1%AA%E5%BA%AD&bi=tg&type=house-pc&pos=data-esf" class="my_address">历下经十路12372号</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="http://sd.esf.sina.com.cn/info/368?bi=tg&type=house-pc&pos=data-esf#wt_source=phb_20_lp" class="imglink" >
                                    <img src="http://i1.esfimg.com/imp/51931d495b455ce346da6ba9366d8099_s155X115_os7e76ea.jpg" title="甸柳小区">
                                                                                                                    <em class="rankNum">5</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="http://sd.esf.sina.com.cn/info/368?bi=tg&type=house-pc&pos=data-esf#wt_source=phb_20_lp" class="prolink">甸柳小区</a>
                                    <span class="loc">历下</span>
                                </p>
                            </div>
                            <p class="price"></p>
                            <p class="up_time">更新</p>
                                                        <a target="_blank" href="http://sd.esf.sina.com.cn/map/?q=%E7%94%B8%E6%9F%B3%E5%B0%8F%E5%8C%BA&bi=tg&type=house-pc&pos=data-esf" class="my_address">燕子山路的路东,文化东...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="http://sd.esf.sina.com.cn/info/716?bi=tg&type=house-pc&pos=data-esf#wt_source=phb_20_lp" class="imglink" >
                                    <img src="http://i3.esfimg.com/imp/51931ce8b4459524ec3c95539d338e9e_s155X115_os78879d.jpg" title="泉星小区">
                                                                                                                    <em class="rankNum">6</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="http://sd.esf.sina.com.cn/info/716?bi=tg&type=house-pc&pos=data-esf#wt_source=phb_20_lp" class="prolink">泉星小区</a>
                                    <span class="loc">天桥</span>
                                </p>
                            </div>
                            <p class="price"></p>
                            <p class="up_time">更新</p>
                                                        <a target="_blank" href="http://sd.esf.sina.com.cn/map/?q=%E6%B3%89%E6%98%9F%E5%B0%8F%E5%8C%BA&bi=tg&type=house-pc&pos=data-esf" class="my_address">济泺路130号</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="http://sd.esf.sina.com.cn/info/95?bi=tg&type=house-pc&pos=data-esf#wt_source=phb_20_lp" class="imglink" >
                                    <img src="http://i2.esfimg.com/imp/51931b7d5845b134e7178c8452c7dd45_s155X115_osebefab.jpg" title="凯旋新城">
                                                                                                                    <em class="rankNum">7</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="http://sd.esf.sina.com.cn/info/95?bi=tg&type=house-pc&pos=data-esf#wt_source=phb_20_lp" class="prolink">凯旋新城</a>
                                    <span class="loc">槐荫</span>
                                </p>
                            </div>
                            <p class="price"></p>
                            <p class="up_time">更新</p>
                                                        <a target="_blank" href="http://sd.esf.sina.com.cn/map/?q=%E5%87%AF%E6%97%8B%E6%96%B0%E5%9F%8E&bi=tg&type=house-pc&pos=data-esf" class="my_address">经十路510号</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="http://sd.esf.sina.com.cn/info/880?bi=tg&type=house-pc&pos=data-esf#wt_source=phb_20_lp" class="imglink" >
                                    <img src="http://i3.esfimg.com/imp/522293b1c385ab9eeb3e85ecb98d1c23_s155X115_os7b4c2a.jpg" title="环山路单位宿舍">
                                                                                                                    <em class="rankNum">8</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="http://sd.esf.sina.com.cn/info/880?bi=tg&type=house-pc&pos=data-esf#wt_source=phb_20_lp" class="prolink">环山路单位宿舍</a>
                                    <span class="loc">历下</span>
                                </p>
                            </div>
                            <p class="price"></p>
                            <p class="up_time">更新</p>
                                                        <a target="_blank" href="http://sd.esf.sina.com.cn/map/?q=%E7%8E%AF%E5%B1%B1%E8%B7%AF%E5%8D%95%E4%BD%8D%E5%AE%BF%E8%88%8D&bi=tg&type=house-pc&pos=data-esf" class="my_address">环山路102号</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="http://sd.esf.sina.com.cn/info/364?bi=tg&type=house-pc&pos=data-esf#wt_source=phb_20_lp" class="imglink" >
                                    <img src="http://i1.esfimg.com/imp/51931da1b105b071260c23c226425ab5_s155X115_os588467.jpg" title="诚基中心">
                                                                                                                    <em class="rankNum">9</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="http://sd.esf.sina.com.cn/info/364?bi=tg&type=house-pc&pos=data-esf#wt_source=phb_20_lp" class="prolink">诚基中心</a>
                                    <span class="loc">历下</span>
                                </p>
                            </div>
                            <p class="price"></p>
                            <p class="up_time">更新</p>
                                                        <a target="_blank" href="http://sd.esf.sina.com.cn/map/?q=%E8%AF%9A%E5%9F%BA%E4%B8%AD%E5%BF%83&bi=tg&type=house-pc&pos=data-esf" class="my_address">和平路47号</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="http://sd.esf.sina.com.cn/info/736?bi=tg&type=house-pc&pos=data-esf#wt_source=phb_20_lp" class="imglink" >
                                    <img src="http://i1.esfimg.com/imp/51931c7a27c597170214f8080e8a819f_s155X115_os7b02ec.jpg" title="金色阳光花园">
                                                                                                                    <em class="rankNum">10</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="http://sd.esf.sina.com.cn/info/736?bi=tg&type=house-pc&pos=data-esf#wt_source=phb_20_lp" class="prolink">金色阳光花园</a>
                                    <span class="loc">天桥</span>
                                </p>
                            </div>
                            <p class="price"></p>
                            <p class="up_time">更新</p>
                                                        <a target="_blank" href="http://sd.esf.sina.com.cn/map/?q=%E9%87%91%E8%89%B2%E9%98%B3%E5%85%89%E8%8A%B1%E5%9B%AD&bi=tg&type=house-pc&pos=data-esf" class="my_address">堤口路177号</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="#wt_source=phb_20_lp" class="imglink" >
                                    <img src="" title="">
                                                                                                                    <em class="rankNum">11</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="#wt_source=phb_20_lp" class="prolink"></a>
                                    <span class="loc"></span>
                                </p>
                            </div>
                            <p class="price"></p>
                            <p class="up_time">更新</p>
                                                        <a target="_blank" href="" class="my_address"></a>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                  </div>
    <!--/ /widget/summary/summary.vm -->
</div>

<a href="javascript:void(0);" class="returnTop upDate" id="back-to-top"  style="display:none;">
    <i></i>
    <span>返回顶部</span>
</a>

<div class="louMessage wmn">
    <table class="louMessage-wrap">
        <tbody>
        <tr>
            <td class="text-title" width="131">推荐信息</td>
            <td class="floor-wrap">
                <span><a href="http://data.house.sina.com.cn/sd/search/h2.html#wt_source=phb_drc_00" target="_blank">济南学区房</a></span>
                <span><a href="http://data.house.sina.com.cn/sd/kaipan/#wt_source=phb_drc_00" target="_blank">济南新开楼盘</a></span>
                <span><a href="http://sd.house.sina.com.cn/exhibit/#wt_source=phb_drc_00" target="_blank">济南房价走势</a></span>
                <span><a href="http://sd.house.sina.com.cn/exhibit/#wt_source=phb_drc_00" target="_blank">济南买房</a></span>
                <span><a href="http://sd.house.sina.com.cn/bbs/#wt_source=phb_drc_00" target="_blank">济南业主社区</a></span>
                <span><a href="http://data.house.sina.com.cn/sd/new/#wt_source=phb_drc_00" target="_blank">济南楼盘</a></span>
                <span><a href="http://sd.house.sina.com.cn/bbs/#wt_source=phb_drc_00" target="_blank">济南买房论坛</a></span>
                <span><a href="http://sd.house.sina.com.cn/exhibit/#wt_source=phb_drc_00" target="_blank">济南楼盘价格</a></span>
                <span><a href="http://sd.house.sina.com.cn/exhibit/#wt_source=phb_drc_00" target="_blank">济南新房</a></span>
            </td>
        </tr>
        </tbody>
    </table>
</div>

<div id="t02" class="fg"></div>
<!--  /widget/footer/footer.vm -->
<!-- 页脚 -->
<div class="footer">
    <p class="d_statem">免责声明：本页面旨在为广大用户提供更多信息的无偿服务；不声明或保证所提供信息的准确性和完整性。本站内所有内容亦不表明本网站之观点或意见,仅供参考和借鉴,购房者在购房时仍需慎重考虑。购房者参考本站信息,进行房屋交易所造成的任何后果与本网站无关，当政府司法机关依照法定程序要求本网站披露个人资料时，我们将根据执法单位之要求或为公共安全之目的提供个人资料。在此情况下之任何披露,本网站均得免责。本页面所提到房屋面积如无特别标示,均指建筑面积。</p>
    <p class="aLink">
        <a target="_blank" href="http://bj.house.sina.com.cn/sina-leju/lj_about.html">关于我们 </a>
        <span>┊</span>
        <a target="_blank" href="http://data.house.sina.com.cn/sd/guide/">楼盘导航 </a>
        <span>┊</span>
        <a rel="nofollow" target="_blank" href="http://my.leju.com/settings/register/indexview/">会员注册</a>
    </p>
    <div class="cFooterInner">
        <p class="copy">Copyright &copy; 1996-2016 SINA Corporation, All Rights Reserved</p>
        <p class="aLink1">乐居房产、家居产品用户服务、产品咨询购买、技术支持客服服务热线：<span>400-606-6969</span></p>
    </div>
</div>
<!-- end页脚 -->
<SCRIPT SRC="http://traffic.house.sina.com.cn/qita_3i3r_tag.js" TYPE="text/javascript"></SCRIPT>

<script type="text/javascript" src="http://cdn.leju.com/newdata.house/201509/LET_newloupan3_0.js" charset="utf-8"></script>

<script type='text/javascript'>

    if(ad_js != '')
    {
        LET.loadScript('http://cdn.leju.com/abp/cmslead_new.js',function(){
            ads.config = {
                host:' http://www.sinaimg.cn/',
                path:'hs/ouyi/lead/src/',
                lunxunList:["t02","t03","t04","t05"]
            };
            LET.loadScript(ad_js,function(){},false,'utf-8');
        },false,'utf-8');
    }

    var winload = new LET.superLazy({
        elems:LET.getElementsByAttribute("img[lsrc]").concat(LET.getElementsByAttribute("iframe[lsrc]")),
        funeles:[],
        container:window,
        islock:false,
        ondataload:function(self,node){
            var src = !+"\v1" ? node['lsrc'] : node.getAttribute('lsrc');
            node.setAttribute("src",src);
            node.removeAttribute("lsrc");
        }
    });

</script><!--/ /widget/footer/footer.vm -->

<script type="text/html" id="line_enlist">
    <div class="cpop cpopform" action="kft_box">
        <input type="hidden" class="kft_aid">
        <input type="hidden" class="kft_token">
        <div class="cpformtit">
            <i class="xikan"></i>
            <span class="context kft_title">报名看房团：新浪乐居专线看房团</span>
        </div>
        <div class="cformcon">
            <ul class="cformlist cformlistcenter">
                <li class="clearfix">
                    <label for="">姓　　名：</label>
                    <div class="cformri">
                        <input type="text" class="intext kft_name">
                    </div>
                </li>
                <li class="clearfix">
                    <label for="">手　　机：</label>
                    <div class="cformri">
                        <input type="text" class="intext kft_mobile">
                    </div>
                </li>
                <li class="clearfix">
                    <label for="">人　　数：</label>
                    <div class="cformri">
                        <div class="cpselect">
                            <span>1人</span>
                            <i class="cpsicon"></i>
                            <ul>
                                <li data-v="1" data-t="1人">1人</li>
                                <li data-v="2" data-t="2人">2人</li>
                                <li data-v="3" data-t="3人">3人</li>
                                <li data-v="4" data-t="4人">4人</li>
                                <li data-v="5" data-t="5人">5人</li>
                                <li data-v="6" data-t="6人">6人</li>
                                <li data-v="7" data-t="7人">7人</li>
                                <li data-v="8" data-t="8人">8人</li>
                                <li data-v="9" data-t="9人">9人</li>
                            </ul>
                        </div>
                        <input type="hidden" class="kft_signupnum" value="1">
                    </div>
                </li>
                <li class="clearfix">
                    <label for="">看房路线：</label>
                    <div class="cformri">
                        <div class="cpselect">
                            <span>1人</span>
                            <i class="cpsicon"></i>
                            <ul>
                                <li>1人</li>
                                <li>2人</li>
                                <li>3人</li>
                            </ul>
                        </div>
                        <input type="hidden" class="kft_lid" value="1" >
                    </div>
                </li>
                <li class="clearfix">
                    <label for="">验 证 码 ：</label>
                    <div class="cformri">
                        <input type="text" class="intextShort kft_mcodel">
                        <span class="btnval1 kft_cbtn1">免费获取</span>
                        <span class="btnval2 kft_cbtn2" style="display:none;">重新获取</span>
                        <span class="btnval3 kft_cbtn3" style="display:none;">已发送(60s)</span>
                        <input type="hidden" class="kft_mcode">
                    </div>
                </li>
            </ul>
        </div>
        <div class="cpoptip">
            <p><em>* </em>姓名和手机号介时将成为确认您身份的唯一方法，请用真实姓名参加活动。</p>
            <p><em>* </em>报名成功后会有乐居工作人员与您确认相关信息，您的信息将之用于参加乐居看房团的活动，乐居将会对您的信息进行保密。</p>
        </div>
        <div class="popbtnwrap">
            <span class="btnred kft_enlist">立即报名</span>
        </div>
        <em class="btnclose kft_close">x</em>
    </div>
</script>
<script type="text/html" id="line_yes">
    <div class="cpop cpoptext">
        <div class="cpopcon clearfix">
            <i class="xisuccess"></i>
            <span class="context">报名成功</span>
        </div>
        <div class="popbtnwrap">
            <span class="btnred kft_close">确 定</span>
        </div>
        <em class="btnclose kft_close">x</em>
    </div>
</script>

<script type="text/javascript" src="http://cdn.leju.com/LET.js"></script>
<script type="text/javascript" src="http://cdn.leju.com/newdata.house/js/hotboard3_0.js" charset="utf-8"></script>
<script type="text/javascript" src="http://cdn.leju.com/newdata.house/201509/city_index.js"></script>
<script>

(function(){

    var bp = document.createElement('script');

    bp.src = '//push.zhanzhang.baidu.com/push.js';

    var s = document.getElementsByTagName("script")[0];

    s.parentNode.insertBefore(bp, s);

})();

</script>
</body>
</html>
'''
resp2='''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=gbk" />
    <title>澳门房价_澳门楼市|楼盘|新房价格|楼盘地图等信息介绍_新浪乐居</title>
    <meta name="Keywords" content="澳门房价,澳门楼市,澳门楼盘,澳门新楼盘,澳门房价走势,澳门新房,澳门楼盘地图,澳门新楼盘信息" />
    <meta name="Description" content="澳门房价，澳门楼市、楼盘、新房价格尽在新浪乐居。提供澳门最新、热门、打折、团购楼盘信息,精美户型图、楼盘地图，澳门房价走势曲线，覆盖全澳门的房地产楼盘数据库。" />
    <meta name="google-site-verification" content="TVYhh8iGMkLFfoPNNQIVjEJO0CkLc61Dl_Upp396xWE" />
    <meta name="robots" content="index, follow" />
    <meta name="googlebot" content="index, follow" />
    <meta http-equiv="X-UA-Compatible" content="IE=EmulateIE7" />
    <meta name="google-site-verification" content="6wVLe2-4RNv4OVwqtedEBEcaMhzgwqz6tknnv0p5qoo" />
    <!--house baidu map coordinate-->
<meta name="location" content="province=澳门;city=澳门;coord=113.54968440007,22.192975956698">
    <link type="text/css" rel="stylesheet"  href="http://data.house.sina.com.cn/css/201509/base.css" source="widget"/>
    <link type="text/css" rel="stylesheet"  href="http://data.house.sina.com.cn/css/201509/header_footer_common.css" source="widget"/>
    <link type="text/css" rel="stylesheet"  href="http://data.house.sina.com.cn/css/201509/city_index.css" source="widget"/>
    <link type="text/css" rel="stylesheet" href="http://cdn.leju.com/121/pcorder/css/ddorder.css">
    <style type="text/css">
        .summary .my_address:hover{color: #ff6666;}
    </style>
    <script type="text/javascript" src="http://cdn.leju.com/jQuery1.8.2.js"></script>
    <script type="text/javascript">
        (function(w){
            w.pageInfo = {
                city: "mc",
                level1_page : 'house',
                level2_page : 'top'
            }
        })(window);
    </script>
</head>
<body>
<div id="t01" class="fg"></div>
<!--  /widget/header/header.vm -->
<script type="text/javascript">
    var cityList = {"as":"\u978d\u5c71","bh":"\u5317\u6d77","bt":"\u5305\u5934","bd":"\u4fdd\u5b9a","bj":"\u5317\u4eac","ba":"\u535a\u9ccc","cz":"\u5e38\u5dde","cs":"\u957f\u6c99","cq":"\u91cd\u5e86","cc":"\u957f\u6625","dl":"\u5927\u8fde","dg":"\u4e1c\u839e","fs":"\u4f5b\u5c71","fz":"\u798f\u5dde","gx":"\u5e7f\u897f","gz":"\u5e7f\u5dde","gl":"\u6842\u6797","gy":"\u8d35\u5dde","ha":"\u54c8\u5c14\u6ee8","hi":"\u6d77\u5357","hf":"\u5408\u80a5","hz":"\u676d\u5dde","hu":"\u547c\u548c\u6d69\u7279","sd":"\u6d4e\u5357","ks":"\u6606\u5c71","kf":"\u5f00\u5c01","yn":"\u6606\u660e","ly":"\u6d1b\u9633","lz":"\u5170\u5dde","nj":"\u5357\u4eac","nc":"\u5357\u660c","nb":"\u5b81\u6ce2","nt":"\u5357\u901a","qd":"\u9752\u5c9b","qi":"\u79e6\u7687\u5c9b","sj":"\u77f3\u5bb6\u5e84","su":"\u82cf\u5dde","sh":"\u4e0a\u6d77","sa":"\u4e09\u4e9a","sz":"\u6df1\u5733","sy":"\u6c88\u9633","sc":"\u56db\u5ddd","ty":"\u592a\u539f","tj":"\u5929\u6d25","ts":"\u5510\u5c71","wu":"\u829c\u6e56","we":"\u5a01\u6d77","wx":"\u65e0\u9521","wh":"\u6b66\u6c49","xm":"\u53a6\u95e8","xz":"\u5f90\u5dde","sx":"\u897f\u5b89","yi":"\u94f6\u5ddd","yt":"\u70df\u53f0","zh":"\u73e0\u6d77","hn":"\u90d1\u5dde","zs":"\u4e2d\u5c71"};
    (function (w) {
        w.pageInfo = {
            city: "mc",
            citycode: "mc",
            column: "",
            root_url: "http://data.house.sina.com.cn"
        }
    })(window);
    var ad_js = '';
</script>
<input type="hidden" id="datacity" value="mc">
<input type="hidden" id="city_en" name="city_en" value="mc">
<input type="hidden" id="datacity_en" name="site" value="mc" >
<input type="hidden" id="citycode" name="citycode" value="mc">
<div class="header">
    <div class="wmn clearfix">
        <a href="http://macao.house.sina.com.cn" class="logo1" target="_blank">Leju logo</a>

        <div id="togglecity" class="select">
            <a class="checkBtn" href="javascript:void(0)">澳门
                                <i class="arrowIco"></i>
                            </a>
                        <div id="contain" class="citypop  none">
                <div class="citypopbd">
                    <div class="searchwra">
                        <div class="clearfix">
                            <input type="text" id="city" class="inputx" placeholder="请输入城市名称"/>
                            <input type="submit" value="搜索" class="submit" id="selcity"/>
                        </div>
                    </div>
                    <div class="citylist">
                        <ul class="engNav clearfix" id="city_tab">
                            <li id="city_tab1" data-tab="#city_tab1_con" data-onclass="cur" class="cur"><a>ABCDFGH</a>
                            </li>
                            <li id="city_tab2" data-tab="#city_tab2_con" data-onclass="cur"><a>JKLNQST</a></li>
                            <li id="city_tab3" data-tab="#city_tab3_con" data-onclass="cur"><a>WXYZ</a></li>
                        </ul>
                                                                        <ul class="cityli" id="city_tab1_con">
                                                                <li>
                                        <strong>A</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/as/" target="_self">鞍山</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>B</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/bh/" target="_self">北海</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/bt/" target="_self">包头</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/bd/" target="_self">保定</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/bj/" target="_self">北京</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/ba/" target="_self">博鳌</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>C</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/cz/" target="_self">常州</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/cs/" target="_self">长沙</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/cq/" target="_self">重庆</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/cc/" target="_self">长春</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>D</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/dl/" target="_self">大连</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/dg/" target="_self">东莞</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>F</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/fs/" target="_self">佛山</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/fz/" target="_self">福州</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>G</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/gx/" target="_self">广西</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/gz/" target="_self">广州</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/gl/" target="_self">桂林</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/gy/" target="_self">贵州</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>H</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/ha/" target="_self">哈尔滨</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/hi/" target="_self">海南</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/hf/" target="_self">合肥</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/hz/" target="_self">杭州</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/hu/" target="_self">呼和浩特</a>
                                                                                                                        </li>
                                                                    </ul>
                                                                                                                    <ul class="cityli none" id="city_tab2_con">
                                                                    <li>
                                        <strong>J</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/sd/" target="_self">济南</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>K</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/ks/" target="_self">昆山</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/kf/" target="_self">开封</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/yn/" target="_self">昆明</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>L</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/ly/" target="_self">洛阳</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/lz/" target="_self">兰州</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>N</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/nj/" target="_self">南京</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/nc/" target="_self">南昌</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/nb/" target="_self">宁波</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/nt/" target="_self">南通</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>Q</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/qd/" target="_self">青岛</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/qi/" target="_self">秦皇岛</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>S</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/sj/" target="_self">石家庄</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/su/" target="_self">苏州</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/sh/" target="_self">上海</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/sa/" target="_self">三亚</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/sz/" target="_self">深圳</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/sy/" target="_self">沈阳</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/sc/" target="_self">四川</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>T</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/ty/" target="_self">太原</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/tj/" target="_self">天津</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/ts/" target="_self">唐山</a>
                                                                                                                        </li>
                                                                    </ul>
                                                                                                                        <ul class="cityli none" id="city_tab3_con">
                                                                        <li>
                                        <strong>W</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/wu/" target="_self">芜湖</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/we/" target="_self">威海</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/wx/" target="_self">无锡</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/wh/" target="_self">武汉</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>X</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/xm/" target="_self">厦门</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/xz/" target="_self">徐州</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/sx/" target="_self">西安</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>Y</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/yi/" target="_self">银川</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/yt/" target="_self">烟台</a>
                                                                                                                        </li>
                                                                                                                                <li>
                                        <strong>Z</strong>
                                                                                                                                    <a ref="nofollow" href="http://data.house.sina.com.cn/zh/" target="_self">珠海</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/hn/" target="_self">郑州</a>
                                                                                                                                                                                <a ref="nofollow" href="http://data.house.sina.com.cn/zs/" target="_self">中山</a>
                                                                                                                        </li>
                                                                    </ul>


                                <div class="btnmorewrap">
                                    <a href="http://macao.house.sina.com.cn/cityguide/" class="btnmore" target="_blank">更多城市<em>
                                        &gt;&gt;</em></a>
                                </div>
                    </div>
                </div>
                <em class="icontri">icon</em>
            </div>
                    </div>
        <ul class="main-nav">
            <li>
                <a href="http://macao.house.sina.com.cn/news/#wt_source=nlpxx_dh1_xw" target="_blank">新闻</a>
            </li>
            <li>
                <a href="http://macao.house.sina.com.cn/exhibit/#wt_source=nlpxx_dh1_xf" target="_blank">新房</a>
            </li>
                        <li>
                <a href="http://www.7gz.com/#wt_source=nlpxx_dh1_zx" target="_blank">装修</a>
            </li>
            <li>
                <a href="http://jiaju.sina.com.cn/#wt_source=nlpxx_dh1_jj" target="_blank">家居</a>
            </li>
            <li>
                <a href="http://fangjs.sina.com.cn/#wt_source=nlpxx_dh1_jr" target="_blank">金融</a>
            </li>
                        <li>
                <a href="http://macao.bbs.house.sina.com.cn/#wt_source=nlpxx_dh1_sq" target="_blank">社区</a>
            </li>
                    </ul>
        <ul id="userlogin" class="login-bar">
            <li class="btn-app"><i class="icon-app"></i>手机版
                <div class="l_ewmBigBox none">
                    <div class="l_erweimaBox">
                        <img src="/images/201509/buyEwm.jpg">
                        <span class="l_mt">下载“<em>乐居买房</em>”</span>
                        <span>随时随地</span>
                        <img src="/images/201509/fontImg.jpg" >
                        <i class="l_poSanjiao1"></i>
                    </div>
                </div>
            </li>

            <li class="btn-login"><a
                    href="http://my.leju.com/" target="_blank"><i
                    class="icon-user"></i>登录</a></li>
            <li class="btn-reg"><span>|</span><a href="http://my.leju.com/settings/register/indexview/" target="_blank">注册</a></li>
        </ul>
        <div id="userinfo" class="none">
            <div class="useriwrap">
                <div class="userinfo">
                    <u class="iuserhead"></u>
                    <span class="usname" id="username"></span>
                    <em><i>◇</i></em>
                    <!-- 用户名需限制字数 -->
                </div>
                <dl class="none">
                    <dd><a href="http://my.leju.com/" target="_blank">帐号设置</a></dd>
                    <dd><a href="http://f.leju.com/" target="_blank">91乐居卡</a></dd>
                    <dd><a href="http://my.leju.com/center/house/index/" target="_blank">已关注的楼盘</a></dd>
                   <!--  <dd><a href="http://macao.bbs.house.sina.com.cn/bbs/space/mycollect?type=1" target="_blank">已收藏的论坛</a></dd> -->
                    <dd><a href="javascript:void(0)" id="userlogout">退出</a></dd>
                </dl>
            </div>
            <ul class="login-bar">
                <li class="btn-app"><i class="icon-app"></i>手机版
                    <div class="l_ewmBigBox none">
                        <div class="l_erweimaBox">
                            <img src="/images/201509/buyEwm.jpg">
                            <span class="l_mt">下载“<em>乐居买房</em>”</span>
                            <span>随时随地</span>
                            <img src="/images/201509/fontImg.jpg" >
                            <i class="l_poSanjiao1"></i>
                        </div>
                    </div>
                </li>
            </ul>
        </div>
    </div>
</div><!--/ /widget/header/header.vm -->

<!--  /widget/search-mod/search-mod.vm -->
<div class="search-mod" id="con_search_1">
    <div class="searchBox">
        <form method="get" action="http://data.house.sina.com.cn/mc/search#wt_source=phb_ss_ss" target="_blank">
            <div class="clearfix">
                <div class="inputBox">
                    <input type="text" class="input" placeholder="请输入楼盘名或楼盘地址" id="s00" name="keyword">
                    <input type="hidden" value="gbk" name="charset">
                     <ul class="inputList none"></ul>
                </div>
                <input type="submit" value="搜 索" class="searchBtn">
                <a href="http://data.house.sina.com.cn/mc/search_advance/#wt_source=phb_ss_gj" class="search01" target="_blank"><i class="searchAd"></i>高级搜索</a>
                <em>|</em>
                <a href="http://map.house.sina.com.cn/mc#wt_source=phb_ss_dt" class="search01" target="_blank"><i class="searchMap"></i>地图找房</a>
            </div>
            <div class="clearfix mt10">
                <select name="district">
                    <option value="0" data-init="区域">区域</option>
                                        <option value="北区">北区</option>
                                        <option value="花王堂区">花王堂区</option>
                                        <option value="中区">中区</option>
                                        <option value="望德堂区">望德堂区</option>
                                        <option value="圣老愣佐堂区">圣老愣佐堂区</option>
                                        <option value="氹仔">氹仔</option>
                                        <option value="路环">路环</option>
                                    </select>
                <select name="pricerange">
                    <option value="0" data-init="价格">价格</option>
                                    </select>
                <select name="housetype">
                    <option value="0" data-init="户型">户型</option>
                                        <option value="一居室">一居室</option>
                                        <option value="二居室">二居室</option>
                                        <option value="三居室">三居室</option>
                                        <option value="四居室">四居室</option>
                                        <option value="五居室">五居室</option>
                                        <option value="六居室">六居室</option>
                                        <option value="七居室">七居室</option>
                                        <option value="复式室">复式室</option>
                                        <option value="跃层">跃层</option>
                                        <option value="楼层平面图">楼层平面图</option>
                                        <option value="别墅">别墅</option>
                                    </select>
                                <select name="hometype">
                    <option value="0" data-init="类型">类型</option>
                                        <option value="60平米以下">60平米以下</option>
                                        <option value="60-90平米">60-90平米</option>
                                        <option value="90-120平米">90-120平米</option>
                                        <option value="120-140平米">120-140平米</option>
                                        <option value="140平米以上">140平米以上</option>
                                    </select>
                <select name="fitment">
                    <option value="0" data-init="装修情况">装修情况</option>
                                    </select>
                <a href="http://data.house.sina.com.cn/mc/search_advance/#wt_source=phb_xx_gd" target="_blank" class="more">更多条件>></a>
            </div>
        </form>
    </div>
</div><!--/ /widget/search-mod/search-mod.vm -->

<!--  /widget/headerNav/headerNav.vm -->
<!--  /widget/headerNav/headerNav.vm -->
<div class="headerNav">
	<div class="news-bg w clearfix">
		<div class="wrap_width clearfix">
		<div class="news-wrap01 clearfix">
			<a href="http://macao.house.sina.com.cn/exhibit#wt_source=phb_dh_100" class="new-icon" target="_blank">
				<i class="dicon01"></i>
				<span>新房中心</span>
			</a>
			<ul class="news-list clearfix">
				<li class="pb">
					<a href="http://data.house.sina.com.cn/mc/kaipan/#wt_source=phb_dh_101" target="_blank">本月开盘</a>
				</li>
				<li class="pb">
					<a href="http://data.house.sina.com.cn/mc/new/#wt_source=phb_dh_102" target="_blank">最新楼盘</a>
				</li>
				<li>
					<a href="http://data.house.sina.com.cn/mc/#wt_source=phb_dh_103" target="_blank">楼盘排行</a>
				</li>
				<li class="pb">
					<a href="http://data.house.sina.com.cn/mc/price/#wt_source=phb_dh_104" target="_blank">涨降价楼盘</a>
				</li>
			</ul>
		</div>
		<div class="news-wrap02 clearfix">
			<a href="http://macao.house.sina.com.cn/scan/#wt_source=phb_dh_200" class="new-icon" target="_blank">
				<i class="dicon02"></i>
				<span>楼盘快讯</span>
			</a>
			<ul class="news-list news-list02 clearfix">
				<li class="pb">
					<a href="http://macao.house.sina.com.cn/scan/kaipan/#wt_source=phb_dh_201" target="_blank">开盘</a>
				</li>
				<li class="pb">
					<a href="http://macao.house.sina.com.cn/scan/xinpan/#wt_source=phb_dh_202" target="_blank">新盘</a>
				</li>
				<li class="pb">
					<a href="http://macao.house.sina.com.cn/scan/dazhe/#wt_source=phb_dh_203" target="_blank">打折</a>
				</li>
				<li>
					<a href="http://macao.house.sina.com.cn/scan/daogou/#wt_source=phb_dh_204" target="_blank">导购</a>
				</li>
			</ul>
		</div>
		<div class="news-wrap03 clearfix">
			<a href="javascript:void (0);" class="new-icon">
				<i class="dicon03"></i>
				<span>乐居为您</span>
			</a>
			<ul class="news-list news-list03 clearfix">
				<li class="pb">
					<a href="http://kft.house.sina.com.cn/mc/index-1.html?ln=phb_dh_mszc" target="_blank">免费看房<span class="s_title"><i class="d_titicon"></i>专车</span></a>
				</li>
				<li class="pb">
					<a href="http://f.leju.com#wt_source=phb_dh_302" target="_blank">会员福利<span class="s_title" target="_blank"><i class="d_titicon"></i>返现</span></a>
				</li>
				<li>
					<a href="http://data.house.sina.com.cn/mc/huxing/#wt_source=phb_dh_303" target="_blank">户型推荐</a>
				</li>
				<li>
					<a href="http://data.house.sina.com.cn/mc/yangban/#wt_source=phb_dh_304" target="_blank">样板间推荐</a>
				</li>
			</ul>
		</div>
		<div class="news-wrap04 clearfix">
			<a href="http://data.house.sina.com.cn/mc/dianping/#wt_source=phb_dh_400" class="new-icon" target="_blank">
				<i class="dicon04"></i>
				<span>楼盘评测</span>
			</a>
			<ul class="news-list clearfix">
				<li class="pb">
					<a href="http://macao.house.sina.com.cn/scan/zbjf/#wt_source=phb_dh_401" target="_blank">主编荐房</a>
				</li>
				<li class="pb">
					<a href="http://data.house.sina.com.cn/mc/tujie/#wt_source=phb_dh_402" target="_blank">图解看房</a>
				</li>
				<li>
					<a href="http://macao.house.sina.com.cn/scan/kfsj/#wt_source=phb_dh_403" target="_blank">看房手记</a>
				</li>
				<li>
            						<a href="http://macao.bbs.house.sina.com.cn/owner/#wt_source=phb_dh_404" target="_blank">业主论坛</a>
            					</li>
			</ul>
		</div>
		</div>
	</div>
</div>
<!--/ /widget/headerNav/headerNav.vm --><!--/ /widget/headerNav/headerNav.vm -->

<div class="crumbs w">
    <a href="http://macao.house.sina.com.cn/#wt_source=phb_mbx_ss" class="crulist">澳门房产</a>
    <em>&gt;</em>
    <a href="http://macao.house.sina.com.cn/exhibit/#wt_source=phb_mbx_ss" class="crulist">新房中心</a>
    <em>&gt;</em>
    <a href="?#wt_source=phb_mbx_ss" class="crulist">楼盘排行</a>
</div>
<div class="w clearfix">

    <!--  /widget/content_left/content_left.vm -->
    <style type="text/css">
    .house_wrap .housewrap2 .inputList {
        position: absolute;
        left: 70px;
        top: 29px;
        border: 1px solid #bfbfbf;
        width: 193px;
        background: #fff;
        z-index: 5;
    }
    .house_wrap .housewrap2 .inputList a {
        display: block;
        height: 30px;
        line-height: 32px;
        padding-left: 10px;
        font-size: 14px;
        color: #666;
    }
    .house_wrap .housewrap2 .inputList a:hover {
        background: #f2f2f2;
    }
</style>
<div class="content_left">
    <div class="ranking">
        <a href="/mc/#wt_source=phb_zphb_00" class="title">楼盘排行热榜<i class="dicon01"></i></a>
        <div class="rank">
            <h3><i class="dicon02"></i>乐居特色榜</h3>
            <ul class="rank_list clearfix">
                                <li >
                                <a href="/mc/kaipan/#wt_source=phb_tsb_01">本月开盘</a>
                                </li>
                                <li >
                                <a href="/mc/new/#wt_source=phb_tsb_02">最新楼盘</a>
                                </li>
                                <li >
                                <a href="/mc/hot/#wt_source=phb_tsb_03">热门楼盘</a>
                                </li>
                                <li >
                                <a href="/mc/?type=search_top#wt_source=phb_tsb_04">搜索热榜</a>
                                </li>
                                <li >
                                <a href="/mc/?type=monthly_clicks#wt_source=phb_tsb_05">本月不可错过</a>
                                </li>
                                <li >
                                <a href="/mc/?type=reside_3_month#wt_source=phb_tsb_06">3个月内入住</a>
                                </li>
                                <li >
                                <a href="/mc/?type=fitment_good#wt_source=phb_tsb_07">精装修</a>
                                </li>
                                <li >
                                <a href="/mc/?type=pinpai_list#wt_source=phb_tsb_08">高性价比</a>
                                </li>
                                <li >
                                <a href="/mc/?type=nearby_trackline#wt_source=phb_tsb_09">地铁沿线</a>
                                </li>
                                <li >
                                <a href="/mc/?type=edu_good#wt_source=phb_tsb_10">教育地产</a>
                                </li>
                                <li >
                                <a href="/mc/?type=region_list#wt_source=phb_tsb_11">区域列表</a>
                                </li>
                                <li >
                                <a href="/mc/?type=pinyin_list#wt_source=phb_tsb_12">拼音列表</a>
                                </li>
                                <li >
                                <a href="/mc/esf/#wt_source=phb_tsb_013">二手房小区</a>
                                </li>
                            </ul>
        </div>
        <div class="rank">
            <h3><i class="dicon03"></i>楼盘户型榜</h3>
            <ul class="rank_list clearfix">
                                <li >
                <a href="/mc/?type=rtype1#wt_source=phb_hx_01">一居</a>
                </li>
                                <li >
                <a href="/mc/?type=rtype2#wt_source=phb_hx_02">两居</a>
                </li>
                            </ul>
        </div>
        <div class="rank">
            <h3><i class="dicon04"></i>楼盘价格榜</h3>
            <ul class="rank_list clearfix">
                                <li >
                <a href="/mc/?type=month_return_3k#wt_source=phb_jg_01">月供3000元以内</a>
                </li>
                            </ul>
        </div>
    </div>
        <div class="house_group">
        <ul class="tab clearfix" id="bookCar">
            <li data-tab="#bookCar_tab1" data-onclass="on" class="on"><a href="#">免费专车看房</a></li>
           </ul>
        <div class="housewrap1" id="bookCar_tab1">
            <ul class="input_list01">
                <li class="clearfix">
                    <label for="" class="label_left">目的楼盘：</label>
                    <input type="text" class="input01" id="s01" autocomplete="off">
                    <input type="hidden" id="hid" name="hid">
                    <input type="hidden" id="zy" name="zy">
                    <div class="inputList none"></div>
                </li>
            </ul>
            <div id="DiDiWrap" order_source="01" yx_act="yx_11"  onclick="javascript:dcsMultiTrack('DCS.dcsuri','/tracelog.htm?act-lp=phb_yc_00','WT.ti','排行榜页跟踪')"></div>
        </div>
    </div>
        <div class="xwph">
        <div class="tit clearfix">
            <span class="floor">楼讯排行</span>
            <a target="_blank" href="http://macao.house.sina.com.cn/scan/" class="more">+ 更多</a>
        </div>
        <div class="xwmain">
            <div class="newsmain">
                <ul class="s_tim clearfix" id="dateNews">
                    <li><a data-tab="#dateNews_tab1" data-onclass="news_cur" href="#" class="news_cur">日</a></li>
                    <li><a data-tab="#dateNews_tab2" data-onclass="news_cur" href="#">周</a></li>
                    <li><a data-tab="#dateNews_tab3" data-onclass="news_cur" href="#">月</a></li>
                </ul>
            </div>
            <ul class="s_nws" id="dateNews_tab1">
                                                <li>
                                                            <i class="renum">1</i>
                                        <a target="_blank" href="http://sz.house.sina.com.cn/scan/lpzj62/#wt_source=phb_zxph_00">坂田规划潜力吸引置业者 三盘比拼谁是最后赢家</a>
                </li>
                                                <li>
                                                            <i class="renum">2</i>
                                        <a target="_blank" href="http://nc.house.sina.com.cn/scan/201602ldfx/#wt_source=phb_zxph_00">2月南昌最热来电TOP10</a>
                </li>
                                                <li>
                                                            <i class="renum">3</i>
                                        <a target="_blank" href="http://nc.house.sina.com.cn/scan/201602cjbd/#wt_source=phb_zxph_00">2016年2月南昌热销楼盘TOP10</a>
                </li>
                                                <li>
                                                            <i>4</i>
                                        <a target="_blank" href="http://sjz.house.sina.com.cn/scan/2016-03-08/09576112788177377094687.shtml#wt_source=phb_zxph_00">曝光在石家庄打死都不能买的楼盘 绝对戳中要害！(组图)</a>
                </li>
                                                <li>
                                                            <i>5</i>
                                        <a target="_blank" href="http://nc.house.sina.com.cn/scan/201603kpyg/#wt_source=phb_zxph_00">3月南昌楼市开盘预告</a>
                </li>
                                                <li>
                                                            <i>6</i>
                                        <a target="_blank" href="http://tj.house.sina.com.cn/scan/2016huijiayouhui/#wt_source=phb_zxph_00">天津回乡置业2016-天津房价</a>
                </li>
                                                <li>
                                                            <i>7</i>
                                        <a target="_blank" href="http://suzhou.house.sina.com.cn/scan/2016-03-07/16146112520653892806668.shtml#wt_source=phb_zxph_00">上周苏州近600套房源加推 投资客组团抢房多盘“秒光”</a>
                </li>
                                                <li>
                                                            <i>8</i>
                                        <a target="_blank" href="http://bj.house.sina.com.cn/scan/2016-03-04/16136111433117187485800.shtml#wt_source=phb_zxph_00">300万是起步价 北京房价全面开涨</a>
                </li>
                                                <li>
                                                            <i>9</i>
                                        <a target="_blank" href="http://hf.house.sina.com.cn/scan/2016-03-08/10166112792923391446726.shtml#wt_source=phb_zxph_00">刚需转移|肥西势头猛烈均价已破8 该出手就出手</a>
                </li>
                                                <li class="lali">
                                                            <i>10</i>
                                        <a target="_blank" href="http://guilin.house.sina.com.cn/scan/2013rollingnews/#wt_source=phb_zxph_00">2013楼市新闻正文页滚动新闻</a>
                </li>
                            </ul>
            <ul class="s_nws none" id="dateNews_tab2">
                                                <li>
                                                            <i class="renum">1</i>
                                        <a target="_blank" href="http://sjz.house.sina.com.cn/scan/2016-03-08/09576112788177377094687.shtml#wt_source=phb_zxph_00">曝光在石家庄打死都不能买的楼盘 绝对戳中要害！(组图)</a>
                </li>
                                                <li>
                                                            <i class="renum">2</i>
                                        <a target="_blank" href="http://hf.house.sina.com.cn/scan/2016-03-08/10166112792923391446726.shtml#wt_source=phb_zxph_00">刚需转移|肥西势头猛烈均价已破8 该出手就出手</a>
                </li>
                                                <li>
                                                            <i class="renum">3</i>
                                        <a target="_blank" href="http://sh.house.sina.com.cn/scan/2016-03-08/06206112512101673384179.shtml#wt_source=phb_zxph_00">9项迪士尼配套市政道路年内开工 含六奉公路</a>
                </li>
                                                <li>
                                                            <i>4</i>
                                        <a target="_blank" href="http://suzhou.house.sina.com.cn/scan/2016-03-08/07006112568766477167412.shtml#wt_source=phb_zxph_00">半月后即涨2000！三月苏城待涨楼盘一览</a>
                </li>
                                                <li>
                                                            <i>5</i>
                                        <a target="_blank" href="http://suzhou.house.sina.com.cn/scan/2016-03-08/07006112557049340815655.shtml#wt_source=phb_zxph_00">3月8号苏州楼市报价 塔园路精装高层均价20000元/平</a>
                </li>
                                                <li>
                                                            <i>6</i>
                                        <a target="_blank" href="http://nc.house.sina.com.cn/scan/2016-03-08/07126112538442380672543.shtml#wt_source=phb_zxph_00">惊呆！南昌楼市7天内十大楼盘涨价 凌晨排队买不到房？</a>
                </li>
                                                <li>
                                                            <i>7</i>
                                        <a target="_blank" href="http://sc.house.sina.com.cn/scan/2016-03-08/06006112505438845328904.shtml#wt_source=phb_zxph_00">成都这些区域天生长得丑如今却惹人爱</a>
                </li>
                                                <li>
                                                            <i>8</i>
                                        <a target="_blank" href="http://guizhou.house.sina.com.cn/scan/2016-03-08/14226112854674510249620.shtml#wt_source=phb_zxph_00">贵阳的女神们原来都住这些地方</a>
                </li>
                                                <li>
                                                            <i>9</i>
                                        <a target="_blank" href="http://cq.house.sina.com.cn/scan/2016-03-08/01026112366586298157187.shtml#wt_source=phb_zxph_00">性别不同怎么买房,论男女在买房上的区别(组图)</a>
                </li>
                                                <li class="lali">
                                                            <i>10</i>
                                        <a target="_blank" href="http://hf.house.sina.com.cn/scan/2016-03-08/10566112803059635899742.shtml#wt_source=phb_zxph_00">“降”难寻？涨不愁卖？2016合肥买房人何去何从？</a>
                </li>
                            </ul>
            <ul class="s_nws none" id="dateNews_tab3">
                                                <li>
                                                            <i class="renum">1</i>
                                        <a target="_blank" href="http://sc.house.sina.com.cn/scan/2016-03-08/07056112501790090255883.shtml#wt_source=phb_zxph_00">2016新政后买房稳赚不亏四大攻略 手把手教你选</a>
                </li>
                                                <li>
                                                            <i class="renum">2</i>
                                        <a target="_blank" href="http://suzhou.house.sina.com.cn/scan/2016-03-08/07006112557049340815655.shtml#wt_source=phb_zxph_00">3月8号苏州楼市报价 塔园路精装高层均价20000元/平</a>
                </li>
                                                <li>
                                                            <i class="renum">3</i>
                                        <a target="_blank" href="http://wh.house.sina.com.cn/scan/2016-03-08/09006112547339657068267.shtml#wt_source=phb_zxph_00">武汉楼市全面爆发 御景星城开启抢购模式(组图)</a>
                </li>
                                                <li>
                                                            <i>4</i>
                                        <a target="_blank" href="http://h.house.sina.com.cn/scan/2016-03-08/08306112533763206735622.shtml#wt_source=phb_zxph_00">2016与你钱包有关的新政 长点心！买套房！</a>
                </li>
                                                <li>
                                                            <i>5</i>
                                        <a target="_blank" href="http://suzhou.house.sina.com.cn/scan/2016-03-08/08006112546467627722820.shtml#wt_source=phb_zxph_00">102，574，1000+……它是如何做到让数字疯狂？</a>
                </li>
                                                <li>
                                                            <i>6</i>
                                        <a target="_blank" href="http://cq.house.sina.com.cn/scan/2016-03-08/01026112366586298157187.shtml#wt_source=phb_zxph_00">性别不同怎么买房,论男女在买房上的区别(组图)</a>
                </li>
                                                <li>
                                                            <i>7</i>
                                        <a target="_blank" href="http://wh.house.sina.com.cn/scan/2016-03-08/09506112544775607729486.shtml#wt_source=phb_zxph_00">买车位就看这两大硬指标(图)</a>
                </li>
                                                <li>
                                                            <i>8</i>
                                        <a target="_blank" href="http://sc.house.sina.com.cn/scan/2016-03-08/06006112505438845328904.shtml#wt_source=phb_zxph_00">成都这些区域天生长得丑如今却惹人爱</a>
                </li>
                                                <li>
                                                            <i>9</i>
                                        <a target="_blank" href="http://suzhou.house.sina.com.cn/scan/2016-03-08/07006112568766477167412.shtml#wt_source=phb_zxph_00">半月后即涨2000！三月苏城待涨楼盘一览</a>
                </li>
                                                <li class="lali">
                                                            <i>10</i>
                                        <a target="_blank" href="http://cs.house.sina.com.cn/scan/2016-03-08/09306112494762336774239.shtml#wt_source=phb_zxph_00">长郡学区精装楼王认筹5千抵6万首付低至两成(图)</a>
                </li>
                            </ul>
        </div>
    </div>
</div>    <!--/ /widget/content_left/content_left.vm -->

    <!--  /widget/summary/summary.vm -->
    <div class="summary">
        <h2 class="sumTit"><em class="none">楼盘排行热榜</em></h2>
                                                                                  <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">最新楼盘</strong>
                                        <span class="titSmall"><em class="xred">TOP 100</em></span>
                                                            <a href="/mc/new/" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc85534/#wt_source=phb_02_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/00/f7/5/45559f4af619f3990e12202b54b_p7_mk7_osb3ef4c_cm320X240.jpg" title="濠庭都會">
                                                                                                                    <em class="rankNumRed">1</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc85534/#wt_source=phb_02_lp" class="prolink">濠庭都會</a>
                                    <span class="loc">氹仔</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>71000</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=85534" class="my_address">乙水仔 低地BT 19/25/30...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc85497/#wt_source=phb_02_lp" class="imglink" >
                                    <img src="http://data.house.sina.com.cn/images/default_m.jpg" title="海擎天">
                                                                                                                    <em class="rankNumRed">2</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc85497/#wt_source=phb_02_lp" class="prolink">海擎天</a>
                                    <span class="loc">中区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>83000</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=85497" class="my_address">澳門林茂堂游艇會傍</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc85484/#wt_source=phb_02_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/2e/9f/c/cc2042d559a2653c3616f07d845_p7_mk7_os47c1ec_cm320X240.jpg" title="海天居">
                                                                                                                    <em class="rankNumRed">3</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc85484/#wt_source=phb_02_lp" class="prolink">海天居</a>
                                    <span class="loc">北区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>81500</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=85484" class="my_address">澳門黑沙環東北大馬路</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc85466/#wt_source=phb_02_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/87/10/4/a4ff2f5d3444c48cc48598a31be_p7_mk7_os5c5470_cm320X240.jpg" title="凱泉灣">
                                                                                                                    <em class="rankNum">4</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc85466/#wt_source=phb_02_lp" class="prolink">凱泉灣</a>
                                    <span class="loc">圣老愣佐堂区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>75000</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=85466" class="my_address">河邊新村94-120號及比厘...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc85069/#wt_source=phb_02_lp" class="imglink" >
                                    <img src="http://cache.house.sina.com.cn/datahouse/22/5b/2553b4c0380bb14fd3e80cc240ea8eb2_320X240.jpg" title="名門世家">
                                                                                                                    <em class="rankNum">5</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc85069/#wt_source=phb_02_lp" class="prolink">名門世家</a>
                                    <span class="loc">氹仔</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>108000</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=85069" class="my_address">氹仔賽馬會對面的背山地...</a>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                                                <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">热门楼盘</strong>
                                        <span class="titSmall"><em class="xred">TOP 100</em></span>
                                                            <a href="/mc/hot/" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc60999/#wt_source=phb_03_lp" class="imglink" >
                                    <img src="http://cache.house.sina.com.cn/datahouse/03/cc/0c82e149df64bcb9dbc8a49e7bdb87c3_320X240.jpg" title="君悅灣">
                                                                                                                    <em class="rankNumRed">1</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc60999/#wt_source=phb_03_lp" class="prolink">君悅灣</a>
                                    <span class="loc">北区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>82400</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <p class="time">共<strong>24730</strong>人感兴趣</p>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc85484/#wt_source=phb_03_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/2e/9f/c/cc2042d559a2653c3616f07d845_p7_mk7_os47c1ec_cm320X240.jpg" title="海天居">
                                                                                                                    <em class="rankNumRed">2</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc85484/#wt_source=phb_03_lp" class="prolink">海天居</a>
                                    <span class="loc">北区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>81500</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <p class="time">共<strong>19829</strong>人感兴趣</p>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc61006/#wt_source=phb_03_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/97/af/2/92a09d34b97ba8832d5304a2215_p7_mk7_os86ad4b_cm320X240.jpg" title="壹號湖畔">
                                                                                                                    <em class="rankNumRed">3</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc61006/#wt_source=phb_03_lp" class="prolink">壹號湖畔</a>
                                    <span class="loc">北区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>121000</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <p class="time">共<strong>19641</strong>人感兴趣</p>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc60997/#wt_source=phb_03_lp" class="imglink" >
                                    <img src="http://cache.house.sina.com.cn/datahouse/3a/66/3679e5acb9fe68aa3a5f1db886268f6a_320X240.jpg" title="金峰南岸">
                                                                                                                    <em class="rankNum">4</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc60997/#wt_source=phb_03_lp" class="prolink">金峰南岸</a>
                                    <span class="loc">北区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>70800</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <p class="time">共<strong>19575</strong>人感兴趣</p>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc60998/#wt_source=phb_03_lp" class="imglink" >
                                    <img src="http://cache.house.sina.com.cn/datahouse/1d/02/10bb4d50abff7dc2c65c13f22c2c792d_320X240.jpg" title="環宇天下">
                                                                                                                    <em class="rankNum">5</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc60998/#wt_source=phb_03_lp" class="prolink">環宇天下</a>
                                    <span class="loc">北区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>72500</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <p class="time">共<strong>18678</strong>人感兴趣</p>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                                                <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">搜索热榜</strong>
                                                            <a href="?type=search_top" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc60999/#wt_source=phb_04_lp" class="imglink" >
                                    <img src="http://cache.house.sina.com.cn/datahouse/03/cc/0c82e149df64bcb9dbc8a49e7bdb87c3_320X240.jpg" title="君悅灣">
                                                                                                                    <em class="rankNumRed">1</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc60999/#wt_source=phb_04_lp" class="prolink">君悅灣</a>
                                    <span class="loc">北区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>82400</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=60999" class="my_address">澳門友誼橋大馬路U+U1地...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc85484/#wt_source=phb_04_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/2e/9f/c/cc2042d559a2653c3616f07d845_p7_mk7_os47c1ec_cm320X240.jpg" title="海天居">
                                                                                                                    <em class="rankNumRed">2</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc85484/#wt_source=phb_04_lp" class="prolink">海天居</a>
                                    <span class="loc">北区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>81500</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=85484" class="my_address">澳門黑沙環東北大馬路</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc61006/#wt_source=phb_04_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/97/af/2/92a09d34b97ba8832d5304a2215_p7_mk7_os86ad4b_cm320X240.jpg" title="壹號湖畔">
                                                                                                                    <em class="rankNumRed">3</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc61006/#wt_source=phb_04_lp" class="prolink">壹號湖畔</a>
                                    <span class="loc">北区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>121000</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=61006" class="my_address">澳門外港新填海區B區B2...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc60997/#wt_source=phb_04_lp" class="imglink" >
                                    <img src="http://cache.house.sina.com.cn/datahouse/3a/66/3679e5acb9fe68aa3a5f1db886268f6a_320X240.jpg" title="金峰南岸">
                                                                                                                    <em class="rankNum">4</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc60997/#wt_source=phb_04_lp" class="prolink">金峰南岸</a>
                                    <span class="loc">北区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>70800</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=60997" class="my_address">路環石排灣馬路聯生填海...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc60998/#wt_source=phb_04_lp" class="imglink" >
                                    <img src="http://cache.house.sina.com.cn/datahouse/1d/02/10bb4d50abff7dc2c65c13f22c2c792d_320X240.jpg" title="環宇天下">
                                                                                                                    <em class="rankNum">5</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc60998/#wt_source=phb_04_lp" class="prolink">環宇天下</a>
                                    <span class="loc">北区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>72500</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=60998" class="my_address">澳門東北大馬路</a>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                                                                                                                                                                                                                                                                                                <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">区域列表</strong>
                                                            <a href="?type=region_list" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc85497/#wt_source=phb_11_lp" class="imglink" >
                                    <img src="http://data.house.sina.com.cn/images/default_m.jpg" title="海擎天">
                                                                                                                    <em class="rankNumRed">1</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc85497/#wt_source=phb_11_lp" class="prolink">海擎天</a>
                                    <span class="loc">中区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>83000</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=85497" class="my_address">澳門林茂堂游艇會傍</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc85466/#wt_source=phb_11_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/87/10/4/a4ff2f5d3444c48cc48598a31be_p7_mk7_os5c5470_cm320X240.jpg" title="凱泉灣">
                                                                                                                    <em class="rankNumRed">2</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc85466/#wt_source=phb_11_lp" class="prolink">凱泉灣</a>
                                    <span class="loc">圣老愣佐堂区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>75000</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=85466" class="my_address">河邊新村94-120號及比厘...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc85063/#wt_source=phb_11_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/03/8a/2/a2dffc02facdb0b03e0080c0f62_p7_mk7_os87c9e1_cm320X240.jpg" title="大潭山壹號">
                                                                                                                    <em class="rankNumRed">3</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc85063/#wt_source=phb_11_lp" class="prolink">大潭山壹號</a>
                                    <span class="loc">氹仔</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>77500</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=85063" class="my_address">澳門氹仔昔日新瞭望臺馬...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc60992/#wt_source=phb_11_lp" class="imglink" >
                                    <img src="http://cache.house.sina.com.cn/datahouse/4c/80/48fb477bf52a5d1de2661509f1108e0c_320X240.jpg" title="天鑽">
                                                                                                                    <em class="rankNum">4</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc60992/#wt_source=phb_11_lp" class="prolink">天鑽</a>
                                    <span class="loc">北区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>126000</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=60992" class="my_address">新口岸皇朝區</a>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                                                <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">拼音列表</strong>
                                                            <a href="?type=pinyin_list" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc61005/#wt_source=phb_12_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/04/8b/a/0adeea0b10c2b2ba7188994aa83_p7_mk7_os986e5c_cm320X240.jpg" title="百利寶花園">
                                                                                                                    <em class="rankNumRed">B</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc61005/#wt_source=phb_12_lp" class="prolink">百利寶花園</a>
                                    <span class="loc">北区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>60000</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=61005" class="my_address">澳門氹仔孫逸仙博士大馬...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc85063/#wt_source=phb_12_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/03/8a/2/a2dffc02facdb0b03e0080c0f62_p7_mk7_os87c9e1_cm320X240.jpg" title="大潭山壹號">
                                                                                                                    <em class="rankNumRed">D</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc85063/#wt_source=phb_12_lp" class="prolink">大潭山壹號</a>
                                    <span class="loc">氹仔</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>77500</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=85063" class="my_address">澳門氹仔昔日新瞭望臺馬...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc85534/#wt_source=phb_12_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/00/f7/5/45559f4af619f3990e12202b54b_p7_mk7_osb3ef4c_cm320X240.jpg" title="濠庭都會">
                                                                                                                    <em class="rankNumRed">H</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc85534/#wt_source=phb_12_lp" class="prolink">濠庭都會</a>
                                    <span class="loc">氹仔</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>71000</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=85534" class="my_address">乙水仔 低地BT 19/25/30...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc60999/#wt_source=phb_12_lp" class="imglink" >
                                    <img src="http://cache.house.sina.com.cn/datahouse/03/cc/0c82e149df64bcb9dbc8a49e7bdb87c3_320X240.jpg" title="君悅灣">
                                                                                                                    <em class="rankNum">J</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc60999/#wt_source=phb_12_lp" class="prolink">君悅灣</a>
                                    <span class="loc">北区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>82400</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=60999" class="my_address">澳門友誼橋大馬路U+U1地...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc85466/#wt_source=phb_12_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/87/10/4/a4ff2f5d3444c48cc48598a31be_p7_mk7_os5c5470_cm320X240.jpg" title="凱泉灣">
                                                                                                                    <em class="rankNum">K</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc85466/#wt_source=phb_12_lp" class="prolink">凱泉灣</a>
                                    <span class="loc">圣老愣佐堂区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>75000</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=85466" class="my_address">河邊新村94-120號及比厘...</a>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                                                                                                                                                                        <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">月供3000元以内</strong>
                                                            <a href="?type=month_return_3k" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc85534/#wt_source=phb_19_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/00/f7/5/45559f4af619f3990e12202b54b_p7_mk7_osb3ef4c_cm320X240.jpg" title="濠庭都會">
                                                                                                                    <em class="rankNumRed">1</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc85534/#wt_source=phb_19_lp" class="prolink">濠庭都會</a>
                                    <span class="loc">氹仔</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>71000</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=85534" class="my_address">乙水仔 低地BT 19/25/30...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc85497/#wt_source=phb_19_lp" class="imglink" >
                                    <img src="http://data.house.sina.com.cn/images/default_m.jpg" title="海擎天">
                                                                                                                    <em class="rankNumRed">2</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc85497/#wt_source=phb_19_lp" class="prolink">海擎天</a>
                                    <span class="loc">中区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>83000</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=85497" class="my_address">澳門林茂堂游艇會傍</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc85069/#wt_source=phb_19_lp" class="imglink" >
                                    <img src="http://cache.house.sina.com.cn/datahouse/22/5b/2553b4c0380bb14fd3e80cc240ea8eb2_320X240.jpg" title="名門世家">
                                                                                                                    <em class="rankNumRed">3</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc85069/#wt_source=phb_19_lp" class="prolink">名門世家</a>
                                    <span class="loc">氹仔</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>108000</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=85069" class="my_address">氹仔賽馬會對面的背山地...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc61006/#wt_source=phb_19_lp" class="imglink" >
                                    <img src="http://src.house.sina.com.cn/imp/imp/deal/97/af/2/92a09d34b97ba8832d5304a2215_p7_mk7_os86ad4b_cm320X240.jpg" title="壹號湖畔">
                                                                                                                    <em class="rankNum">4</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc61006/#wt_source=phb_19_lp" class="prolink">壹號湖畔</a>
                                    <span class="loc">北区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>121000</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=61006" class="my_address">澳門外港新填海區B區B2...</a>
                                                    </li>
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="/mc61004/#wt_source=phb_19_lp" class="imglink" >
                                    <img src="http://cache.house.sina.com.cn/datahouse/36/d2/3dce0478d0608931c53d05596acd2726_320X240.jpg" title="鳳凰臺">
                                                                                                                    <em class="rankNum">5</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>正在办理中
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="/mc61004/#wt_source=phb_19_lp" class="prolink">鳳凰臺</a>
                                    <span class="loc">北区</span>
                                </p>
                            </div>
                            <p class="price">价格约<strong>52900</strong>元/平米</p>
                            <p class="up_time">02月11日更新</p>
                                                        <a target="_blank" href="http://map.house.sina.com.cn/bj/index.php?type=h&hid=61004" class="my_address">新口岸</a>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                                                <div class="sumUnit">
                <div class="sumUtit">
                    <strong class="tit">二手房小区</strong>
                                        <span class="titSmall"><em class="xred">TOP 100</em></span>
                                                            <a href="/mc/esf/" class="btnmore">更多 &gt;</a>
                                    </div>
                <div class="sumCon">
                    <ul class="clearfix">
                                                <li>
                            <div class="imgwrap">
                                <a target="_blank" href="#wt_source=phb_20_lp" class="imglink" >
                                    <img src="" title="">
                                                                                                                    <em class="rankNumRed">1</em>
                                                                                                                <i class="yszIcon" onmouseover="$(this).next().show();"></i>
                                    <div class="yszShow none" onmouseout="$(this).hide();">
                                        <div class="yszI158">
                                            <p class="fontS">
                                                <i></i>
                                            </p>
                                        </div>
                                    </div>
                                </a>
                                <p class="bgcon">
                                    <a target="_blank" href="#wt_source=phb_20_lp" class="prolink"></a>
                                    <span class="loc"></span>
                                </p>
                            </div>
                            <p class="price"></p>
                            <p class="up_time">更新</p>
                                                        <a target="_blank" href="" class="my_address"></a>
                                                    </li>
                                            </ul>
                </div>
            </div>
                                  </div>
    <!--/ /widget/summary/summary.vm -->
</div>

<a href="javascript:void(0);" class="returnTop upDate" id="back-to-top"  style="display:none;">
    <i></i>
    <span>返回顶部</span>
</a>

<div class="louMessage wmn">
    <table class="louMessage-wrap">
        <tbody>
        <tr>
            <td class="text-title" width="131">推荐信息</td>
            <td class="floor-wrap">
                <span><a href="http://data.house.sina.com.cn/mc/search/h2.html#wt_source=phb_drc_00" target="_blank">澳门学区房</a></span>
                <span><a href="http://data.house.sina.com.cn/mc/kaipan/#wt_source=phb_drc_00" target="_blank">澳门新开楼盘</a></span>
                <span><a href="http://macao.house.sina.com.cn/exhibit/#wt_source=phb_drc_00" target="_blank">澳门房价走势</a></span>
                <span><a href="http://macao.house.sina.com.cn/exhibit/#wt_source=phb_drc_00" target="_blank">澳门买房</a></span>
                <span><a href="http://macao.house.sina.com.cn/bbs/#wt_source=phb_drc_00" target="_blank">澳门业主社区</a></span>
                <span><a href="http://data.house.sina.com.cn/mc/new/#wt_source=phb_drc_00" target="_blank">澳门楼盘</a></span>
                <span><a href="http://macao.house.sina.com.cn/bbs/#wt_source=phb_drc_00" target="_blank">澳门买房论坛</a></span>
                <span><a href="http://macao.house.sina.com.cn/exhibit/#wt_source=phb_drc_00" target="_blank">澳门楼盘价格</a></span>
                <span><a href="http://macao.house.sina.com.cn/exhibit/#wt_source=phb_drc_00" target="_blank">澳门新房</a></span>
            </td>
        </tr>
        </tbody>
    </table>
</div>

<div id="t02" class="fg"></div>
<!--  /widget/footer/footer.vm -->
<!-- 页脚 -->
<div class="footer">
    <p class="d_statem">免责声明：本页面旨在为广大用户提供更多信息的无偿服务；不声明或保证所提供信息的准确性和完整性。本站内所有内容亦不表明本网站之观点或意见,仅供参考和借鉴,购房者在购房时仍需慎重考虑。购房者参考本站信息,进行房屋交易所造成的任何后果与本网站无关，当政府司法机关依照法定程序要求本网站披露个人资料时，我们将根据执法单位之要求或为公共安全之目的提供个人资料。在此情况下之任何披露,本网站均得免责。本页面所提到房屋面积如无特别标示,均指建筑面积。</p>
    <p class="aLink">
        <a target="_blank" href="http://bj.house.sina.com.cn/sina-leju/lj_about.html">关于我们 </a>
        <span>┊</span>
        <a target="_blank" href="http://data.house.sina.com.cn/mc/guide/">楼盘导航 </a>
        <span>┊</span>
        <a rel="nofollow" target="_blank" href="http://my.leju.com/settings/register/indexview/">会员注册</a>
    </p>
    <div class="cFooterInner">
        <p class="copy">Copyright &copy; 1996-2016 SINA Corporation, All Rights Reserved</p>
        <p class="aLink1">乐居房产、家居产品用户服务、产品咨询购买、技术支持客服服务热线：<span>400-606-6969</span></p>
    </div>
</div>
<!-- end页脚 -->
<SCRIPT SRC="http://traffic.house.sina.com.cn/qita_3i3r_tag.js" TYPE="text/javascript"></SCRIPT>

<script type="text/javascript" src="http://cdn.leju.com/newdata.house/201509/LET_newloupan3_0.js" charset="utf-8"></script>

<script type='text/javascript'>

    if(ad_js != '')
    {
        LET.loadScript('http://cdn.leju.com/abp/cmslead_new.js',function(){
            ads.config = {
                host:' http://www.sinaimg.cn/',
                path:'hs/ouyi/lead/src/',
                lunxunList:["t02","t03","t04","t05"]
            };
            LET.loadScript(ad_js,function(){},false,'utf-8');
        },false,'utf-8');
    }

    var winload = new LET.superLazy({
        elems:LET.getElementsByAttribute("img[lsrc]").concat(LET.getElementsByAttribute("iframe[lsrc]")),
        funeles:[],
        container:window,
        islock:false,
        ondataload:function(self,node){
            var src = !+"\v1" ? node['lsrc'] : node.getAttribute('lsrc');
            node.setAttribute("src",src);
            node.removeAttribute("lsrc");
        }
    });

</script><!--/ /widget/footer/footer.vm -->

<script type="text/html" id="line_enlist">
    <div class="cpop cpopform" action="kft_box">
        <input type="hidden" class="kft_aid">
        <input type="hidden" class="kft_token">
        <div class="cpformtit">
            <i class="xikan"></i>
            <span class="context kft_title">报名看房团：新浪乐居专线看房团</span>
        </div>
        <div class="cformcon">
            <ul class="cformlist cformlistcenter">
                <li class="clearfix">
                    <label for="">姓　　名：</label>
                    <div class="cformri">
                        <input type="text" class="intext kft_name">
                    </div>
                </li>
                <li class="clearfix">
                    <label for="">手　　机：</label>
                    <div class="cformri">
                        <input type="text" class="intext kft_mobile">
                    </div>
                </li>
                <li class="clearfix">
                    <label for="">人　　数：</label>
                    <div class="cformri">
                        <div class="cpselect">
                            <span>1人</span>
                            <i class="cpsicon"></i>
                            <ul>
                                <li data-v="1" data-t="1人">1人</li>
                                <li data-v="2" data-t="2人">2人</li>
                                <li data-v="3" data-t="3人">3人</li>
                                <li data-v="4" data-t="4人">4人</li>
                                <li data-v="5" data-t="5人">5人</li>
                                <li data-v="6" data-t="6人">6人</li>
                                <li data-v="7" data-t="7人">7人</li>
                                <li data-v="8" data-t="8人">8人</li>
                                <li data-v="9" data-t="9人">9人</li>
                            </ul>
                        </div>
                        <input type="hidden" class="kft_signupnum" value="1">
                    </div>
                </li>
                <li class="clearfix">
                    <label for="">看房路线：</label>
                    <div class="cformri">
                        <div class="cpselect">
                            <span>1人</span>
                            <i class="cpsicon"></i>
                            <ul>
                                <li>1人</li>
                                <li>2人</li>
                                <li>3人</li>
                            </ul>
                        </div>
                        <input type="hidden" class="kft_lid" value="1" >
                    </div>
                </li>
                <li class="clearfix">
                    <label for="">验 证 码 ：</label>
                    <div class="cformri">
                        <input type="text" class="intextShort kft_mcodel">
                        <span class="btnval1 kft_cbtn1">免费获取</span>
                        <span class="btnval2 kft_cbtn2" style="display:none;">重新获取</span>
                        <span class="btnval3 kft_cbtn3" style="display:none;">已发送(60s)</span>
                        <input type="hidden" class="kft_mcode">
                    </div>
                </li>
            </ul>
        </div>
        <div class="cpoptip">
            <p><em>* </em>姓名和手机号介时将成为确认您身份的唯一方法，请用真实姓名参加活动。</p>
            <p><em>* </em>报名成功后会有乐居工作人员与您确认相关信息，您的信息将之用于参加乐居看房团的活动，乐居将会对您的信息进行保密。</p>
        </div>
        <div class="popbtnwrap">
            <span class="btnred kft_enlist">立即报名</span>
        </div>
        <em class="btnclose kft_close">x</em>
    </div>
</script>
<script type="text/html" id="line_yes">
    <div class="cpop cpoptext">
        <div class="cpopcon clearfix">
            <i class="xisuccess"></i>
            <span class="context">报名成功</span>
        </div>
        <div class="popbtnwrap">
            <span class="btnred kft_close">确 定</span>
        </div>
        <em class="btnclose kft_close">x</em>
    </div>
</script>

<script type="text/javascript" src="http://cdn.leju.com/LET.js"></script>
<script type="text/javascript" src="http://cdn.leju.com/newdata.house/js/hotboard3_0.js" charset="utf-8"></script>
<script type="text/javascript" src="http://cdn.leju.com/newdata.house/201509/city_index.js"></script>
<script>

(function(){

    var bp = document.createElement('script');

    bp.src = '//push.zhanzhang.baidu.com/push.js';

    var s = document.getElementsByTagName("script")[0];

    s.parentNode.insertBefore(bp, s);

})();

</script>
</body>
</html>
'''

def clean(resp):
    re0 = re.sub(r'<!DOCTYPE.*>', '', resp)
    re0 = re.sub(r'<!--.*>','',re0)
    re0 = re.sub(r'<input.*>','',re0)
    re0 = re.sub(r'<\s+', '<', re0)
    re0 = re.sub(r'\s+>', '>', re0)
    # print "re0:",re0
    re1 = re.sub(r'(?<=>)([^<]*)(?=<)', '', re0)
    # print "re1:",re1
    pattern0 = re.compile(r'(<\w+)(\s+[^>]+)')
    re2 = pattern0.sub(r'\1', re1)
    # print "re2:",re2
    re3 = re.sub(r'<option>.*?</option>', '', re2)
    re3 = re.sub(r'<li>.*?</li>', '', re3)
    re3 = re.sub(r'<script>.*?</script>', '', re3)
    re3 = re.sub(r'<SCRIPT>.*?</SCRIPT>', '', re3)
    # print "re3:",re3
    return re3

def isSamePage(url1, url2):
    document_root1 = html.fromstring(url1)
    tree1 = etree.tostring(document_root1, encoding='unicode', pretty_print=True)

    document_root1 = html.fromstring(url1)
    tree2 = etree.tostring(document_root1, encoding='unicode', pretty_print=True)

    return tree1, tree2

if __name__ == '__main__':
    print "resp1:", clean(resp1)
    print "resp2:", clean(resp2)

