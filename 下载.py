import sys
import os
import re
import psutil
import ctypes
import subprocess
import requests
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QProgressBar, QPushButton,
    QComboBox, QTextEdit, QFileDialog, QLabel, QHeaderView, QLineEdit
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QSize
from PyQt6.QtGui import QFont, QColor
# 捕获requests各类异常
from requests.exceptions import RequestException, ConnectionError, Timeout, HTTPError

# -------------------------- 核心配置：100+软件库+一键下载方案+流氓软件库 --------------------------
# 1. 常用软件官网直链库（7大分类+游戏工具，100+款，官网直链无捆绑）
SOFTWARE_LIB = {
    "办公软件": [
        {"name": "WPS Office 电脑版", "desc": "免费办公套件，替代Microsoft Office", "url": "https://wdl1.cache.wps.cn/wpsdl/wpsoffice/download/win/wps_office_11.1.0.14358.exe", "filename": "WPS_Office.exe"},
        {"name": "LibreOffice", "desc": "开源免费跨平台办公套件", "url": "https://download.documentfoundation.org/libreoffice/stable/24.2.1/win/x86_64/LibreOffice_24.2.1_Win_x64.msi", "filename": "LibreOffice_24.2.1.msi"},
        {"name": "印象笔记", "desc": "跨平台云笔记工具", "url": "https://cdn.yinxiang.com/desktop/public/YinxiangBiji_win_3.8.2.1064.exe", "filename": "印象笔记.exe"},
        {"name": "有道云笔记", "desc": "网易旗下云笔记，支持多端同步", "url": "https://note.youdao.com/youdaoNote/win64/YoudaoNote.exe", "filename": "有道云笔记.exe"},
        {"name": "XMind 2024", "desc": "高颜值思维导图工具", "url": "https://dl2.xmind.cn/XMind-for-Windows-24.01.2421.exe", "filename": "XMind_2024.exe"},
        {"name": "MindMaster", "desc": "国产思维导图，模板丰富", "url": "https://www.edrawsoft.com.cn/download/mindmaster/mindmaster_win.exe", "filename": "MindMaster.exe"},
        {"name": "金山文档", "desc": "在线办公桌面端，多人协作", "url": "https://kdocs.cn/download/desktop/KDocs_Win.exe", "filename": "金山文档.exe"},
        {"name": "腾讯文档", "desc": "腾讯在线办公，微信/QQ联动", "url": "https://docs.qq.com/desktop/TencentDocs.exe", "filename": "腾讯文档.exe"},
        {"name": "永中Office", "desc": "国产跨平台办公软件，自主内核", "url": "https://www.yozocloud.cn/static/yozo-office/setup/YozoOffice.exe", "filename": "永中Office.exe"},
        {"name": "幕布", "desc": "大纲笔记+思维导图，极简风", "url": "https://mubu.com/download/MubuSetup.exe", "filename": "幕布.exe"},
    ],
    "开发工具": [
        {"name": "Python 3.12", "desc": "Python最新稳定版（64位）", "url": "https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe", "filename": "Python3.12.3.exe"},
        {"name": "VS Code 最新版", "desc": "微软轻量代码编辑器，跨平台", "url": "https://vscode.download.prss.microsoft.com/dbazure/download/stable/ee2b180d582a7f601fa6ecfdad8d9fd269ab1884/VSCodeUserSetup-x64-1.85.1.exe", "filename": "VSCode.exe"},
        {"name": "Git 64位", "desc": "分布式版本控制工具，开发必备", "url": "https://github.com/git-for-windows/git/releases/download/v2.45.0.windows.1/Git-2.45.0-64-bit.exe", "filename": "Git.exe"},
        {"name": "PyCharm Community", "desc": "Python专属IDE（免费社区版）", "url": "https://download.jetbrains.com/python/pycharm-community-2024.1.exe", "filename": "PyCharm_Community.exe"},
        {"name": "Notepad++", "desc": "轻量代码编辑器，替代记事本", "url": "https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v8.6.4/npp.8.6.4.Installer.exe", "filename": "Notepad++.exe"},
        {"name": "Postman", "desc": "API接口调试工具，开发必备", "url": "https://dl.pstmn.io/download/latest/win64", "filename": "Postman.exe"},
        {"name": "MySQL Workbench", "desc": "MySQL数据库可视化管理工具", "url": "https://cdn.mysql.com/Downloads/MySQLGUITools/mysql-workbench-community-8.0.37-winx64.msi", "filename": "MySQL_Workbench.exe"},
        {"name": "Node.js 22", "desc": "JavaScript运行时，前端开发必备", "url": "https://nodejs.org/dist/v22.2.0/node-v22.2.0-x64.msi", "filename": "NodeJS22.exe"},
        {"name": "Cmder", "desc": "高颜值Windows终端，替代CMD", "url": "https://github.com/cmderdev/cmder/releases/download/v1.3.20/cmder.zip", "filename": "Cmder.zip"},
    ],
    "影音软件": [
        {"name": "PotPlayer 64位", "desc": "全能视频播放器，无广告", "url": "https://file.naver.com/potplayer/PotPlayerSetup64.exe", "filename": "PotPlayer64.exe"},
        {"name": "VLC 播放器", "desc": "开源全能播放器，支持所有格式", "url": "https://get.videolan.org/vlc/3.0.21/win64/vlc-3.0.21-win64.exe", "filename": "VLC.exe"},
        {"name": "QQ音乐 电脑版", "desc": "腾讯音乐，曲库丰富", "url": "https://y.qq.com/portal/download.html", "filename": "QQ音乐.exe"},
        {"name": "网易云音乐", "desc": "网易音乐，个性化推荐", "url": "https://music.163.com/#/download", "filename": "网易云音乐.exe"},
        {"name": "B站客户端", "desc": "哔哩哔哩电脑版，4K播放", "url": "https://www.bilibili.com/download/app/pc/latest.html", "filename": "B站客户端.exe"},
        {"name": "剪映专业版", "desc": "抖音旗下视频剪辑，免费易用", "url": "https://www.capcut.cn/desktop", "filename": "剪映专业版.exe"},
        {"name": "格式工厂", "desc": "免费音视频格式转换，无广告", "url": "https://www.pc6.com/soft/119019.html", "filename": "格式工厂.exe"},
        {"name": "Audacity", "desc": "开源音频编辑工具，免费专业", "url": "https://github.com/audacity/audacity/releases/download/Audacity-3.5.1/audacity-win-3.5.1-x64.exe", "filename": "Audacity.exe"},
    ],
    "社交软件": [
        {"name": "微信电脑版", "desc": "腾讯微信PC端，扫码登录", "url": "https://pc.weixin.qq.com/cgi-bin/readtemplate?t=winpc_new/client_download&lang=zh_CN", "filename": "微信电脑版.exe"},
        {"name": "QQ 电脑版", "desc": "腾讯QQ最新版，64位", "url": "https://im.qq.com/pcqq/download.html", "filename": "QQ电脑版.exe"},
        {"name": "钉钉PC版", "desc": "阿里旗下办公社交，团队协作", "url": "https://www.dingtalk.com/download", "filename": "钉钉.exe"},
        {"name": "企业微信", "desc": "腾讯旗下企业办公社交", "url": "https://work.weixin.qq.com/wework_admin/register?from=myhome", "filename": "企业微信.exe"},
        {"name": "飞书PC版", "desc": "字节旗下办公社交，多维表格", "url": "https://www.feishu.cn/download", "filename": "飞书.exe"},
        {"name": "TIM", "desc": "腾讯轻量QQ，办公专用", "url": "https://im.qq.com/tim/download.html", "filename": "TIM.exe"},
        {"name": "YY语音", "desc": "语音社交，游戏开黑必备", "url": "https://www.yy.com/download/", "filename": "YY语音.exe"},
    ],
    "实用工具": [
        {"name": "7-Zip", "desc": "免费解压工具，支持所有格式", "url": "https://www.7-zip.org/a/7z2407-x64.exe", "filename": "7-Zip.exe"},
        {"name": "WinRAR", "desc": "经典解压工具，兼容ZIP/RAR", "url": "https://www.win-rar.com/fileadmin/winrar-versions/winrar/winrar-x64-701sc.exe", "filename": "WinRAR.exe"},
        {"name": "迅雷11", "desc": "经典下载工具，支持多协议", "url": "https://www.xunlei.com/download.html", "filename": "迅雷11.exe"},
        {"name": "Everything", "desc": "极速文件搜索工具，秒搜", "url": "https://www.voidtools.com/downloads/", "filename": "Everything.exe"},
        {"name": "Listary", "desc": "文件搜索/快速启动，增强Everything", "url": "https://www.listary.com/download/", "filename": "Listary.exe"},
        {"name": "Snipaste", "desc": "高颜值截图工具，支持贴图", "url": "https://www.snipaste.com/download.html", "filename": "Snipaste.exe"},
        {"name": "鲁大师", "desc": "硬件检测/跑分/温度监控", "url": "https://www.ludashi.com/download.html", "filename": "鲁大师.exe"},
        {"name": "驱动精灵", "desc": "国产驱动管理，一键更新", "url": "https://www.drivergenius.com/", "filename": "驱动精灵.exe"},
        {"name": "CCleaner", "desc": "国际系统清理工具，轻量无广告", "url": "https://www.ccleaner.com/ccleaner/download/standard", "filename": "CCleaner.exe"},
    ],
    "浏览器": [
        {"name": "Chrome 谷歌浏览器", "desc": "国际主流浏览器，速度快", "url": "https://dl.google.com/tag/s/dl/chrome/install/googlechromestandaloneenterprise64.msi", "filename": "Chrome.exe"},
        {"name": "Edge 微软浏览器", "desc": "Windows自带，基于Chromium", "url": "https://www.microsoft.com/zh-cn/edge/download?form=MA13FJ", "filename": "Edge.exe"},
        {"name": "Firefox 火狐浏览器", "desc": "开源浏览器，注重隐私", "url": "https://download.mozilla.org/?product=firefox-latest&os=win64&lang=zh-CN", "filename": "Firefox.exe"},
        {"name": "360极速浏览器", "desc": "基于Chromium，国产优化", "url": "https://browser.360.cn/ee/", "filename": "360极速浏览器.exe"},
        {"name": "QQ浏览器", "desc": "腾讯旗下，与QQ/微信联动", "url": "https://browser.qq.com/down.html", "filename": "QQ浏览器.exe"},
        {"name": "Brave 浏览器", "desc": "注重隐私，无广告", "url": "https://brave.com/zh-CN/download/", "filename": "Brave.exe"},
    ],
    "设计软件": [
        {"name": "Figma 客户端", "desc": "UI/UX设计，团队协作", "url": "https://www.figma.com/downloads/", "filename": "Figma.exe"},
        {"name": "Canva 可画", "desc": "在线设计，模板丰富，免费", "url": "https://www.canva.cn/download/", "filename": "Canva.exe"},
        {"name": "创客贴", "desc": "国产在线设计，极简易用", "url": "https://www.chuangkit.com/download", "filename": "创客贴.exe"},
        {"name": "Axure RP 10", "desc": "原型设计工具，产品经理必备", "url": "https://www.axure.com/download", "filename": "AxureRP10.exe"},
        {"name": "墨刀", "desc": "国产原型设计，免费轻量", "url": "https://modao.cc/download", "filename": "墨刀.exe"},
        {"name": "GIMP", "desc": "开源图片处理，免费替代PS", "url": "https://www.gimp.org/downloads/", "filename": "GIMP.exe"},
        {"name": "Inkscape", "desc": "开源矢量设计，免费替代AI", "url": "https://inkscape.org/zh-hans/download/windows/", "filename": "Inkscape.exe"},
    ],
    "游戏工具": [
        {"name": "Steam 客户端", "desc": "全球最大游戏平台", "url": "https://cdn.akamai.steamstatic.com/client/installer/SteamSetup.exe", "filename": "Steam.exe"},
        {"name": "WeGame 腾讯游戏平台", "desc": "腾讯游戏一站式平台", "url": "https://wegame.qq.com/download.shtml", "filename": "WeGame.exe"},
        {"name": "雷神加速器", "desc": "游戏网络加速，支持多款网游", "url": "https://www.leigod.com/download/", "filename": "雷神加速器.exe"},
        {"name": "网易UU加速器", "desc": "网易游戏加速，免费体验", "url": "https://uu.163.com/download.html", "filename": "网易UU加速器.exe"},
    ]
}

# 2. 一键下载方案配置（新机开荒/游戏下载/开发必备/办公必备）- 匹配SOFTWARE_LIB的软件名
DOWNLOAD_PLANS = {
    "新机开荒": [
        "Edge 微软浏览器", "WPS Office 电脑版", "微信电脑版", "QQ 电脑版",
        "7-Zip", "Everything", "Snipaste", "PotPlayer 64位", "迅雷11"
    ],
    "游戏下载": [
        "Steam 客户端", "WeGame 腾讯游戏平台", "PotPlayer 64位", "YY语音",
        "迅雷11", "360极速浏览器", "Snipaste", "CCleaner"
    ],
    "开发必备": [
        "Python 3.12", "VS Code 最新版", "Git 64位", "PyCharm Community",
        "Notepad++", "Postman", "MySQL Workbench", "Cmder", "Edge 微软浏览器"
    ],
    "办公必备": [
        "WPS Office 电脑版", "微信电脑版", "企业微信", "钉钉PC版",
        "印象笔记", "XMind 2024", "金山文档", "Edge 微软浏览器", "Snipaste"
    ]
}

# 3. 常见流氓软件库（Windows）- 进程名/软件名/卸载关键词
ROGUE_SOFTWARE = [
    {"name": "2345全家桶", "process": ["2345explorer", "2345pcsafe", "2345accelerator"], "uninst_key": "2345"},
    {"name": "金山毒霸", "process": ["kavstart", "kavsvc", "kdbsvc"], "uninst_key": "金山毒霸"},
    {"name": "360顽固插件", "process": ["360tray", "360safe", "360sd"], "uninst_key": "360"},
    {"name": "百度全家桶", "process": ["baiduwenku", "baiduyun", "baidufm"], "uninst_key": "百度"},
    {"name": "鲁大师顽固版", "process": ["ludashi", "ludashiem"], "uninst_key": "鲁大师"},
    {"name": "驱动精灵捆绑版", "process": ["drivergenius", "dgupdate"], "uninst_key": "驱动精灵"},
    {"name": "快压", "process": ["kuaizip", "kzservice"], "uninst_key": "快压"},
    {"name": "酷我音乐捆绑版", "process": ["kuwoMusic", "kuwosvc"], "uninst_key": "酷我音乐"},
    {"name": "酷狗音乐捆绑版", "process": ["kugou", "kgmusic"], "uninst_key": "酷狗音乐"},
    {"name": "暴风影音广告版", "process": ["baofeng", "bfplayer"], "uninst_key": "暴风影音"},
]

# 基础配置
TOTAL_SOFT = sum([len(softs) for softs in SOFTWARE_LIB.values()])  # 软件总数
DEFAULT_DOWNLOAD_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "常用软件下载")  # 默认下载路径
IS_WINDOWS = sys.platform == "win32"  # 判断是否为Windows系统（流氓软件卸载仅支持Windows）

# -------------------------- 多线程下载类：支持单文件/批量队列下载 --------------------------
class DownloadThread(QThread):
    progress_signal = pyqtSignal(int)  # 更新进度(百分比)
    log_signal = pyqtSignal(str)       # 打印日志
    finish_signal = pyqtSignal(bool, str)  # 下载完成/失败（是否成功，软件名）

    def __init__(self, soft_name, url, save_path, filename):
        super().__init__()
        self.soft_name = soft_name
        self.url = url
        self.save_path = save_path
        self.filename = filename
        self.is_running = True

    def run(self):
        """核心下载逻辑：分块流式下载，防反爬，异常处理"""
        try:
            # 创建保存目录
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)
                self.log_signal.emit(f"【{self.soft_name}】创建下载目录：{self.save_path}")

            full_path = os.path.join(self.save_path, self.filename)
            # 防重复下载
            if os.path.exists(full_path):
                self.log_signal.emit(f"【{self.soft_name}】文件已存在，跳过下载")
                self.finish_signal.emit(True, self.soft_name)
                return

            # 模拟浏览器请求，允许重定向
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            }
            # 获取文件大小
            file_size = 0
            try:
                head_resp = requests.head(self.url, headers=headers, timeout=10, allow_redirects=True)
                head_resp.raise_for_status()
                file_size = int(head_resp.headers.get("Content-Length", 0))
            except:
                self.log_signal.emit(f"【{self.soft_name}】无法获取文件大小，显示实时下载进度")

            # 流式下载（1MB分块）
            self.log_signal.emit(f"【{self.soft_name}】开始下载，保存路径：{full_path}")
            with requests.get(self.url, headers=headers, stream=True, timeout=30, allow_redirects=True) as resp:
                resp.raise_for_status()
                chunk_size = 1024 * 1024
                downloaded_size = 0
                with open(full_path, "wb+") as f:
                    for chunk in resp.iter_content(chunk_size=chunk_size):
                        if not self.is_running:
                            f.close()
                            if os.path.exists(full_path):
                                os.remove(full_path)  # 删除未完成文件
                            self.log_signal.emit(f"【{self.soft_name}】下载被取消")
                            self.finish_signal.emit(False, self.soft_name)
                            return
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            # 更新进度
                            if file_size > 0:
                                progress = int((downloaded_size / file_size) * 100)
                                self.progress_signal.emit(progress)
                            else:
                                self.progress_signal.emit((downloaded_size // chunk_size) % 100)

            # 下载完成
            self.log_signal.emit(f"【{self.soft_name}】下载完成！文件路径：{full_path}")
            self.progress_signal.emit(100)
            self.finish_signal.emit(True, self.soft_name)

        except Exception as e:
            err_msg = str(e)[:50] if str(e) else "未知错误"
            self.log_signal.emit(f"【{self.soft_name}】下载失败：{err_msg}")
            self.finish_signal.emit(False, self.soft_name)

    def stop_download(self):
        """停止下载"""
        self.is_running = False

# -------------------------- 流氓软件处理类：搜索+卸载（Windows专属） --------------------------
class RogueSoftwareHandler:
    @staticmethod
    def is_admin():
        """判断是否为管理员权限"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    @staticmethod
    def search_rogue():
        """搜索本地流氓软件：返回{软件名: 是否运行}"""
        rogue_result = {}
        running_processes = [p.name().lower() for p in psutil.process_iter()]
        for rogue in ROGUE_SOFTWARE:
            rogue_name = rogue["name"]
            is_running = False
            # 检测进程是否运行
            for proc in rogue["process"]:
                if proc.lower() in running_processes:
                    is_running = True
                    break
            rogue_result[rogue_name] = is_running
        return rogue_result

    @staticmethod
    def kill_process(rogue):
        """结束流氓软件进程"""
        killed = []
        for proc_name in rogue["process"]:
            try:
                for p in psutil.process_iter():
                    if p.name().lower() == proc_name.lower():
                        p.terminate()
                        p.wait(timeout=5)
                        killed.append(proc_name)
            except:
                continue
        return killed

    @staticmethod
    def uninstall_rogue(rogue_key):
        """调用Windows官方卸载命令"""
        try:
            # Windows自带卸载命令（wmic）
            cmd = f'wmic product where "name like \'%{rogue_key}%\'" call uninstall /nointeractive'
            subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            return True
        except:
            return False

    @staticmethod
    def onekey_uninstall():
        """一键卸载所有检测到的流氓软件"""
        if not IS_WINDOWS:
            return False, "仅支持Windows系统"
        if not RogueSoftwareHandler.is_admin():
            return False, "需要管理员权限，请右键以管理员运行程序"

        rogue_list = ROGUE_SOFTWARE
        result = []
        for rogue in rogue_list:
            # 1. 结束进程
            killed_procs = RogueSoftwareHandler.kill_process(rogue)
            # 2. 卸载软件
            is_uninst = RogueSoftwareHandler.uninstall_rogue(rogue["uninst_key"])
            # 3. 记录结果
            if killed_procs or is_uninst:
                result.append(f"{rogue['name']}：结束进程{str(killed_procs)}，卸载{('成功' if is_uninst else '失败')}")
            else:
                result.append(f"{rogue['name']}：未检测到运行，无需卸载")
        return True, "\n".join(result)

# -------------------------- 主窗口类：PyQt6 UI + 所有功能整合 --------------------------
class SoftDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"常用软件下载器 - 共{TOTAL_SOFT}款（官网直链+流氓软件清理）")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 700)

        # 全局变量：核心状态+映射
        self.download_path = DEFAULT_DOWNLOAD_PATH
        self.current_category = "全部"  # 修改1：默认选中“全部”分类
        self.search_key = ""  # 搜索关键词
        self.progress_bar_map = {}  # 软件名->进度条
        self.download_thread = None  # 当前下载线程
        self.batch_queue = []  # 批量下载队列
        self.rogue_handler = RogueSoftwareHandler()  # 流氓软件处理器

        # 初始化UI
        self.init_ui()
        # 加载初始软件列表
        self.load_soft_list(self.current_category)

    def init_ui(self):
        """初始化UI：新增搜索框/一键方案/流氓软件区，融合原有布局"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 字体配置
        font_title = QFont("微软雅黑", 12, QFont.Weight.Bold)
        font_normal = QFont("微软雅黑", 10)
        font_small = QFont("微软雅黑", 9)

        # -------------------------- 顶部：标题+核心功能按钮 --------------------------
        top_layout = QHBoxLayout()
        # 标题
        title_label = QLabel(f"电脑常用软件下载器（{TOTAL_SOFT}款官网直链）| 流氓软件一键清理")
        title_label.setFont(font_title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 基础功能按钮
        self.select_path_btn = QPushButton("选择下载路径")
        self.open_path_btn = QPushButton("打开下载目录")
        for btn in [self.select_path_btn, self.open_path_btn]:
            btn.setFont(font_normal)
            btn.setFixedSize(QSize(120, 35))
        # 一键下载方案按钮组
        plan_btns = {}
        for plan_name in DOWNLOAD_PLANS.keys():
            btn = QPushButton(plan_name)
            btn.setFont(font_normal)
            btn.setFixedSize(QSize(100, 35))
            btn.clicked.connect(lambda _, p=plan_name: self.batch_download(p))
            plan_btns[plan_name] = btn
        # 布局拼接
        top_layout.addWidget(title_label)
        top_layout.addStretch()
        for btn in plan_btns.values():
            top_layout.addWidget(btn)
        top_layout.addWidget(self.select_path_btn)
        top_layout.addWidget(self.open_path_btn)
        main_layout.addLayout(top_layout)

        # -------------------------- 中部上：分类筛选+搜索框 --------------------------
        filter_layout = QHBoxLayout()
        # 分类筛选
        filter_label = QLabel("软件分类：")
        filter_label.setFont(font_normal)
        self.category_combo = QComboBox()
        self.category_combo.setFont(font_normal)
        # 修改2：先添加“全部”选项，再添加原有分类
        self.category_combo.addItem("全部")  
        self.category_combo.addItems(SOFTWARE_LIB.keys())
        self.category_combo.currentTextChanged.connect(self.on_category_change)
        # 搜索框
        search_label = QLabel("搜索软件：")
        search_label.setFont(font_normal)
        self.search_edit = QLineEdit()
        self.search_edit.setFont(font_normal)
        self.search_edit.setPlaceholderText("输入软件名/简介，实时全局模糊搜索（不区分大小写）")
        self.search_edit.setFixedHeight(35)
        self.search_edit.textChanged.connect(self.on_search)
        # 清空搜索按钮
        self.clear_search_btn = QPushButton("清空")
        self.clear_search_btn.setFont(font_small)
        self.clear_search_btn.setFixedSize(QSize(60, 35))
        self.clear_search_btn.clicked.connect(lambda: self.search_edit.setText(""))
        # 布局拼接
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.category_combo)
        filter_layout.addSpacing(20)
        filter_layout.addWidget(search_label)
        filter_layout.addWidget(self.search_edit)
        filter_layout.addWidget(self.clear_search_btn)
        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)

        # -------------------------- 中部中：软件表格（核心） --------------------------
        self.soft_table = QTableWidget()
        self.soft_table.setColumnCount(4)
        self.soft_table.setHorizontalHeaderLabels(["软件名称", "软件简介", "操作", "下载进度"])
        self.soft_table.setFont(font_normal)
        # 列宽配置（PyQt6标准：Stretch替代Expanding）
        self.soft_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.soft_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.soft_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.soft_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.soft_table.setColumnWidth(0, 200)
        self.soft_table.setColumnWidth(2, 100)
        # 表格样式
        self.soft_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.soft_table.verticalHeader().setDefaultSectionSize(40)
        main_layout.addWidget(self.soft_table)

        # -------------------------- 中部下：流氓软件一键处理区 --------------------------
        rogue_layout = QVBoxLayout()
        rogue_title = QLabel("📌 流氓软件一键清理区（Windows专属）")
        rogue_title.setFont(font_title)
        rogue_title.setStyleSheet("color: #d9534f;")
        # 流氓软件功能按钮+结果显示
        rogue_func_layout = QHBoxLayout()
        self.rogue_search_btn = QPushButton("一键搜索流氓软件")
        self.rogue_uninst_btn = QPushButton("一键卸载所有流氓软件")
        for btn in [self.rogue_search_btn, self.rogue_uninst_btn]:
            btn.setFont(font_normal)
            btn.setFixedSize(QSize(150, 35))
            btn.setStyleSheet("background-color: #f8d7da; color: #d9534f; border: 1px solid #ebccd1;")
        # 流氓软件结果显示
        self.rogue_result_edit = QTextEdit()
        self.rogue_result_edit.setFont(font_small)
        self.rogue_result_edit.setReadOnly(True)
        self.rogue_result_edit.setPlaceholderText("流氓软件搜索/卸载结果将显示在这里...")
        self.rogue_result_edit.setFixedHeight(80)
        # 布局拼接
        rogue_func_layout.addWidget(self.rogue_search_btn)
        rogue_func_layout.addWidget(self.rogue_uninst_btn)
        rogue_func_layout.addStretch()
        rogue_layout.addWidget(rogue_title)
        rogue_layout.addLayout(rogue_func_layout)
        rogue_layout.addWidget(self.rogue_result_edit)
        main_layout.addLayout(rogue_layout)

        # -------------------------- 底部：下载日志区 --------------------------
        log_layout = QVBoxLayout()
        log_title = QLabel("📝 下载日志（实时更新，带时间戳）")
        log_title.setFont(font_title)
        self.log_text = QTextEdit()
        self.log_text.setFont(font_small)
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("下载/操作日志将显示在这里...")
        log_layout.addWidget(log_title)
        log_layout.addWidget(self.log_text)
        main_layout.addLayout(log_layout)

        # -------------------------- 信号槽绑定：所有按钮/输入框 --------------------------
        # 基础功能
        self.select_path_btn.clicked.connect(self.choose_download_path)
        self.open_path_btn.clicked.connect(self.open_download_path)
        # 搜索功能
        self.clear_search_btn.clicked.connect(lambda: self.search_edit.setText(""))
        # 流氓软件处理
        self.rogue_search_btn.clicked.connect(self.search_rogue_soft)
        self.rogue_uninst_btn.clicked.connect(self.uninstall_rogue_soft)

        # 初始化日志
        self.add_log(f"程序启动成功！默认下载路径：{self.download_path}")
        self.add_log(f"共加载{TOTAL_SOFT}款常用软件，所有链接均为官网直链！")
        if not IS_WINDOWS:
            self.add_log("⚠ 非Windows系统，流氓软件清理功能不可用！")

    # -------------------------- 核心功能：软件列表加载+搜索+分类（适配“全部”分类） --------------------------
    def on_category_change(self, category):
        """分类切换回调"""
        self.current_category = category
        self.load_soft_list(category)

    def on_search(self, text):
        """搜索框实时输入回调"""
        self.search_key = text.strip().lower()
        self.load_soft_list(self.current_category)

    def load_soft_list(self, category):
        """加载软件列表：适配“全部”分类 + 全局搜索"""
        # 1. 有搜索关键词：从所有分类的软件中全局筛选（不受分类影响）
        if self.search_key:
            all_softs = []
            for cate in SOFTWARE_LIB.values():  # 遍历所有分类，收集全部软件
                all_softs.extend(cate)
            # 全局过滤：匹配名称/简介，不区分大小写
            softs = [
                s for s in all_softs
                if self.search_key in s["name"].lower() or self.search_key in s["desc"].lower()
            ]
        # 2. 无搜索关键词：根据分类加载
        else:
            # 修改3：选中“全部”则加载所有软件，否则加载对应分类
            if category == "全部":
                softs = []
                for cate in SOFTWARE_LIB.values():
                    softs.extend(cate)
            else:
                softs = SOFTWARE_LIB.get(category, [])

        # 清空表格+进度条映射
        self.soft_table.setRowCount(len(softs))
        self.progress_bar_map.clear()

        # 填充表格
        for row, soft in enumerate(softs):
            name, desc = soft["name"], soft["desc"]
            # 软件名
            name_item = QTableWidgetItem(name)
            name_item.setFont(QFont("微软雅黑", 10))
            self.soft_table.setItem(row, 0, name_item)
            # 软件简介
            desc_item = QTableWidgetItem(desc)
            desc_item.setFont(QFont("微软雅黑", 9))
            self.soft_table.setItem(row, 1, desc_item)
            # 下载按钮
            down_btn = QPushButton("开始下载")
            down_btn.setFixedSize(80, 30)
            down_btn.setFont(QFont("微软雅黑", 9))
            down_btn.clicked.connect(lambda _, s=soft: self.start_download(s))
            self.soft_table.setCellWidget(row, 2, down_btn)
            # 进度条
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(0)
            progress_bar.setFormat("%p%")
            self.soft_table.setCellWidget(row, 3, progress_bar)
            # 进度条映射（关键：确保所有软件都能绑定进度条）
            self.progress_bar_map[name] = progress_bar

        # 日志提示优化：区分场景
        if self.search_key:
            self.add_log(f"全局搜索关键词「{self.search_key}」，共找到{len(softs)}款软件（跨所有分类）")
        else:
            if category == "全部":
                self.add_log(f"加载【全部】分类，共{len(softs)}款软件（所有分类汇总）")
            else:
                self.add_log(f"加载【{category}】分类，共{len(softs)}款软件")

    # -------------------------- 核心功能：下载路径管理 --------------------------
    def choose_download_path(self):
        """选择自定义下载路径"""
        path = QFileDialog.getExistingDirectory(self, "选择下载目录", self.download_path)
        if path:
            self.download_path = path
            self.add_log(f"✅ 已修改下载路径为：{self.download_path}")

    def open_download_path(self):
        """打开下载目录"""
        try:
            if not os.path.exists(self.download_path):
                os.makedirs(self.download_path)
                self.add_log(f"📁 下载目录不存在，已自动创建：{self.download_path}")
            os.startfile(self.download_path)
            self.add_log(f"📁 已打开下载目录：{self.download_path}")
        except Exception as e:
            self.add_log(f"❌ 打开下载目录失败：{str(e)[:30]}")

    # -------------------------- 核心功能：单文件下载+批量队列下载 --------------------------
    def start_download(self, soft, is_batch=False):
        """开始下载：单文件/批量队列"""
        soft_name, soft_url, soft_filename = soft["name"], soft["url"], soft["filename"]
        progress_bar = self.progress_bar_map.get(soft_name)
        if not progress_bar:
            self.add_log(f"❌ 【{soft_name}】未找到进度条，下载失败")
            return

        # 停止当前正在运行的下载
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop_download()
            self.download_thread.wait()
            self.add_log(f"🔴 已停止上一个下载任务，启动新任务：{soft_name}")

        # 重置进度条
        progress_bar.setValue(0)
        # 创建并启动下载线程
        self.download_thread = DownloadThread(soft_name, soft_url, self.download_path, soft_filename)
        self.download_thread.progress_signal.connect(progress_bar.setValue)
        self.download_thread.log_signal.connect(self.add_log)
        # 批量下载则绑定队列回调，否则绑定普通回调
        if is_batch:
            self.download_thread.finish_signal.connect(self.batch_download_next)
        else:
            self.download_thread.finish_signal.connect(self.download_finish)
        self.download_thread.start()
        self.add_log(f"🟢 【{soft_name}】已启动下载线程！")

    def download_finish(self, is_success, soft_name):
        """单文件下载完成回调"""
        self.add_log(f"{'✅' if is_success else '❌'} 【{soft_name}】下载任务{'完成' if is_success else '失败'}")
        self.download_thread = None

    def batch_download(self, plan_name):
        """一键方案批量下载：初始化队列"""
        self.batch_queue = DOWNLOAD_PLANS.get(plan_name, [])
        if not self.batch_queue:
            self.add_log(f"❌ 一键方案「{plan_name}」无软件，下载失败")
            return
        # 过滤队列中不存在的软件
        all_soft_names = [s["name"] for cate in SOFTWARE_LIB.values() for s in cate]
        self.batch_queue = [name for name in self.batch_queue if name in all_soft_names]
        if not self.batch_queue:
            self.add_log(f"❌ 一键方案「{plan_name}」中无有效软件")
            return
        # 日志提示
        self.add_log(f"🟢 启动一键下载方案「{plan_name}」，共{len(self.batch_queue)}款软件：{str(self.batch_queue)}")
        # 启动第一个软件下载
        self.batch_download_next(True, "")

    def batch_download_next(self, is_prev_success, prev_soft):
        """批量下载队列：下一个软件"""
        if prev_soft:
            self.add_log(f"🔄 【{prev_soft}】下载完成，准备下载下一个软件...")
        # 队列空则结束
        if not self.batch_queue:
            self.add_log(f"✅ 所有批量下载任务完成！")
            self.download_thread = None
            return
        # 取出队列第一个软件
        current_soft_name = self.batch_queue.pop(0)
        # 查找软件信息
        current_soft = None
        for cate in SOFTWARE_LIB.values():
            for s in cate:
                if s["name"] == current_soft_name:
                    current_soft = s
                    break
            if current_soft:
                break
        # 启动下载（标记为批量）
        self.start_download(current_soft, is_batch=True)

    # -------------------------- 核心功能：流氓软件搜索+卸载 --------------------------
    def search_rogue_soft(self):
        """一键搜索流氓软件"""
        if not IS_WINDOWS:
            res = "❌ 仅支持Windows系统！"
            self.rogue_result_edit.setText(res)
            self.add_log(res)
            return
        # 执行搜索
        rogue_result = self.rogue_handler.search_rogue()
        res_text = []
        for name, is_running in rogue_result.items():
            res_text.append(f"{name}：{'🟡 正在运行' if is_running else '🟢 未检测到'}")
        # 显示结果
        self.rogue_result_edit.setText("\n".join(res_text))
        self.add_log("✅ 流氓软件搜索完成，结果如上")

    def uninstall_rogue_soft(self):
        """一键卸载流氓软件"""
        # 执行卸载
        is_success, res = self.rogue_handler.onekey_uninstall()
        # 显示结果
        self.rogue_result_edit.setText(res)
        if is_success:
            self.add_log("✅ 流氓软件一键卸载完成，结果如上")
        else:
            self.add_log(f"❌ 流氓软件卸载失败：{res}")
            self.rogue_result_edit.setStyleSheet("color: #d9534f;")

    # -------------------------- 工具方法：日志添加+窗口关闭事件 --------------------------
    def add_log(self, content):
        """添加日志：带时间戳，自动滚动到底部"""
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_content = f"[{time_str}] {content}"
        self.log_text.append(log_content)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def closeEvent(self, event):
        """窗口关闭：停止正在下载的线程"""
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop_download()
            self.download_thread.wait()
            self.add_log("🔴 程序关闭，已停止当前下载任务")
        self.add_log("👋 程序正常退出，感谢使用！")
        event.accept()

# -------------------------- 程序入口：适配Python3.9+PyQt6 --------------------------
if __name__ == "__main__":
    # 适配PyQt6高DPI+中文显示
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    # 平台插件路径适配（Python3.9）
    try:
        import PyQt6.Qt6 as Qt6
        os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.dirname(Qt6.__file__) + "/plugins/platforms"
    except:
        pass
    # 启动程序
    app = QApplication(sys.argv)
    window = SoftDownloader()
    window.show()
    sys.exit(app.exec())
