# Podriver: Practical Online Disaster Reduction Intelligence ViewER
**P**ractical **O**nline **D**isaster **R**eduction **I**ntelligence **V**iew**ER**
实用的在线减灾情报查看器（破实通览）

[![Powered by Project Podris](https://uy.wzznft.com/i/2025/05/04/khy721.png "Powered by Project Podris")](https://podris.longecko.group/)

## 项目简介 Project Introduction
Project Introduction
本项目是[Project Podris](https://podris.longecko.group/)旗下的基于[Flet](https://flet.dev/)框架开发的一款桌面端纯Python防震减灾情报查看器，旨在为用户提供更专业准确全面的防灾情报浏览环境。<br>
This project is a desktop-only Python earthquake prevention and disaster reduction intelligence viewer developed under the [Project Podris](https://podris.longecko.group/) and based on the [Flet](https://flet.dev/) framework. It aims to provide users with a more professional, accurate, and comprehensive environment for browsing disaster prevention intelligence.

## 功能特性 Features
- 多源情报聚合: 支持从多个数据源获取地震预警、地震报告、摇晃感知等信息，并进行整合展示。<br>
  Multiple source aggregation: Supports obtaining earthquake warnings, reports, and shaking perception information from multiple sources and presenting them in a unified manner.
- 烈度信息展示: 可展示地震预警预估烈度、地震报告观测烈度、摇晃感知实测烈度等信息，震灾情况一目了然。<br>
  Intensity information display: Displays earthquake warning estimated intensity, earthquake report observed intensity, and shaking perception measured intensity, making earthquake disaster situation clear.
- 地震波可视化: 提供基于tjma2001走时表的实时地震波绘制功能，帮助用户更好地观测地震实况。<br>
  Earthquake wave visualization: Provides real-time earthquake wave drawing based on the tjma2001 travel time table, helping users better observe earthquake conditions.
- 音效与TTS: 使用PodriverTones音效，同时支持由EdgeTTS驱动的灾情语音播报，灾情灾况皆可“闻”。<br>
  Sound effects and TTS: Uses PodriverTones sound effects, and supports disaster announcements driven by EdgeTTS, making disaster conditions "hearable".
- 跨平台兼容性: 得益于Flet与Python的强大，Podriver支持在Windows、Linux、macOS主流操作系统上运行。<br>
  Cross-platform compatibility: Thanks to the powerful combination of Flet and Python, Podriver can run on Windows, Linux, and macOS.

## 快速上手 Quick Start
### 环境要求 Environment requirements
- 操作系统: Windows 10 1909 64位 或更高版本，Debian Linux 11 64位 或更高版本（或者其它在2020年后发布的主流Linux64位发行版），macOS 10.15（Catalina） 或更高版本。<br>
  Operating system: Windows 10 1909 64-bit or higher, Debian Linux 11 64-bit or higher (or any mainstream 64-bit Linux distribution released after 2020), or macOS 10.15 (Catalina) or higher.
- 处理器: 4 个物理内核或以上，每核基准速度 2.0 GHz 或更高。<br>
  Processor: At least 4 physical cores, with a base speed of 2.0 GHz or higher per core.
- 运行内存: 8 GB 物理内存 或以上。<br>
  Memory: At least 8 GB of physical memory.
- 磁盘空间: 空闲 10 GB 或以上。<br>
  Disk space: At least 10 GB free.
- 网络连接: 位于中国大陆内的主流运营商以太网或无线局域网连接。至少需要 20 Mbps 的下行带宽与 10 Mbps 的上行带宽（禁止任何代理与VPN）。<br>
  Network connection: Mainline operators in China. At least 20 Mbps of upstream bandwidth and 10 Mbps of downstream bandwidth (prohibits any proxy or VPN).
- 用户: 10 岁及以上的有国籍自然人，要求具备良好的价值观与道德准则，能独立查阅文档解决问题或礼貌提问，并兼具良好的自我反省能力。<br>
  User: A 10-year-old with a nationality, who is a citizen and has good values and moral principles, can independently consult documentation to solve problems or ask questions politely, and has good self-reflection abilities.
### 使用发布版本 Use the release version:
您可以从官方 GitHub 仓库的 [发布页面](https://github.com/Avastrator/Podriver/releases) 或 [硌漆数字资源目录中心](https://catalog.longecko.group/) 获取适用于您平台的可执行程序，解压后运行主程序，完成配置即可。<br>
You can obtain the executable program for your platform from either the [Releases page](https://github.com/Avastrator/Podriver/releases) of the official GitHub repository or the [Longecko Group Resource Catalog Center](https://catalog.longecko.group/). After decompressing it, run the main program and complete the configuration.
### 使用源码运行 Use source code to run:
克隆这个仓库 Clone this repository:
```bash
git clone https://github.com/Avastrator/Podriver.git
```
安装依赖 Install dependencies:
```bash
pip install -r requirements.txt
```
运行应用 Run the application:
```bash
flet run Podriver
```

## 编译打包 Compile and package:
我们建议使用flet build工具进行打包，详见[Flet 文档](https://flet.dev/docs/publish)。<br>
We recommend using the flet build tool for packaging. For details, see the [Flet Documentation](https://flet.dev/docs/publish).

## 目录结构 Directory structure
    ├── README.md  // 本README文档 This README document
    ├── LICENSE  // 开源许可证 Open source license
    ├── pyproject.toml  // 项目配置文件 Project configuration file
    └── src  // 项目源代码 Source code
        ├── main.py  // 主程序入口 Main program entry
        ├── LGK_Podriver_UI_Main.py  // 主界面UI Main UI
        ├── LGK_Podriver_UI_OOBE.py  // 首次运行界面UI First run UI
        ├── LGK_Podriver_Args.py  // 环境变量存放器 Environment variable holder
        ├── LGK_Podriver_IO_Logger.py  // 日志记录器 Logger
        ├── LGK_Podriver_Receiver.py  // 情报接收模块 Intelligence receiving module
        ├── InterfaceHandlers  // 界面（情报）处理模块 UI(Information) processing module
            ├── LGK_Podriver_Audio.py  // 音频模块 Audio module
            ├── LGK_Podriver_EEWHandler.py  // 地震预警模块 Earthquake early warning module
            ├── LGK_Podriver_EQRHandler.py  // 地震报告模块 Earthquake report module
            ├── LGK_Podriver_ESPHandler.py  // 摇晃感知模块 Earthquake Shaking Perception module
            ├── LGK_Podriver_WaveHandler.py  // 地震波模块 Earthquake wave module
            └── LGK_Podriver_MapFocusManager.py  // 地图焦点（轮播）管理模块 Map focus (carousel) management module
        └── assets  // 静态资源 Static resources
            ├── icon.png  // 应用图标 Application icon
            ├── lang.json  // 语言包 Language file
            ├── config.example  // 原始配置文件 Original configuration file
            ├── traveltimetable.json  // 地震波走时表（tjma2001） Earthquake wave travel time table(tjma2001)
            ├── fonts  // 字体文件 Font files
            ├── audio  // 音频文件 Audio files
            ├── intensity_icons  // 烈度图标 Earthquake intensity icons
            ├── intensity_round_icons  // 圆版烈度图标 Earthquake intensity round icons
            ├── map_icons  // 地图标记图标 Map mark icons
            └── station_icons  // 摇晃感知站点图标 Shake perception station icons

## 许可证 License
Podriver的所有组件均采用[木兰宽松许可证，第二版](http://license.coscl.org.cn/MulanPSL2)开源。<br>
All components of Podriver are open-sourced under the [Mulan Permissive Software License, Version 2](http://license.coscl.org.cn/MulanPSL2).