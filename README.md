# bilibiliblackdynamic_id
过期动态筛选，输出id，存放到同目录生成的id文档里。
需要firfox浏览器与配套的driver，抓取元素如果更换浏览器可能不适用。
使用步骤：
1.安装python解释器，最好安装我开发时用的3.7版本，避免版本不同依赖库不兼容
2.安装完毕后找到python.exe所在文件夹，在地址栏输入cmd，输入pip install -r requirements.txt -U -i http://pypi.tuna.tsinghua.edu.cn/simple 
3.将geckodriver.exe拖入C盘根目录，下载配套的82.0.3 (64 位)的Firefox浏览器
4.安装thonny或者PyCharm或者vscode或者anaconda(个人推荐vscode或者thonny，前者万能，后者小巧)
5.使用上述其中一个软件打开并运行(电脑内存不够的可以忽略第三步，直接在cmd里输入python B站动态删除.py)
6.等待页面弹出，待页面弹出到手机app扫描二维码登陆时，扫描登陆或进行其他登陆操作(这一段你只有20秒时间登陆，如果需要延长这一步的等待时间，请在代码里修改"#第一步等待时长")
7.其他时间与循环设置可以在B站动态删除.py里修改，注意我的注释即可。(可以选择输出为文档还是输出到cmd/软件控制台)
