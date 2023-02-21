# Newdao 词典，a new version of Wudao-dict

**本项目修改自 [Wudao-dict](https://github.com/ChestnutHeng/Wudao-dict)**

## 有哪些新特性?
1. 修改了资源文件的访问方式以及程序运行的方式，Linux 端现在通过简单的 `python setup.py install` 可将该项目作为 Python 包安装到包目录，并自动安装 `nd` 运行脚本。安装完成后运行 `nd hello` 即可看到词义，无需 root 权限。
2. 修改了服务运行的方式，Windows 端可通过运行批处理文件 `start.bat` 运行服务，但需要定位到 `main.py` 文件所在位置手动运行 `python main.py hello` 获得词义。

更多功能等我有时间摸鱼再继续修改。
