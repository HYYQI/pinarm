# 包管理
## 设计
- 三部分：[管理器](#管理器pinarm)，[执行器](#执行器)，[拦截器](#拦截器)
- 以debian生态为基础，借用apt做包管理基础

### 管理器pinarm
- 安装的包分为系统包和软件包
    - 系统包
        - 直接安装到系统中，由apt操作
        - 没有隔离，由pinarm和apt共同记录
        - 由apt管理
    - 软件包
        - 在/Applications目录中隔离安装运行
        - chroot容器化，无法直接访问真实文件系统
        - 由pinarm管理，通过apt源安装
        - 依赖由pinarm处理
- 软件包环境隔离
    - 每个软件通过chroot运行
    - 软件包安装到/Applications/<包名>/
    - 软件包元信息在软件包根目录下DEEBIAN目录保留
    - 依赖通过软/硬连接接入
    - 软件包执行由[执行器](#执行器)处理
    - 执行过程中操作由[拦截器](#拦截器)处理
- pinarm代理apt操作并记录
- pinarm需要记录所有已安装的包，记录已安装的文件
- pinarm维护一份公共索引数据库
#### pinarm数据库
- 记录所有已安装的包信息
> 包名，版本，大小，DEBIAN位置，安装时间，包类型
- 记录所有已安装的文件 -> 树形结构
> 以包为单位记录文件列表：<br>
>   跟踪所有文件更改实时更新<br>
>   数据由拦截器和pinarm本身提供
- 记录所有存在在Applications下的文件的综合数据库
- 维护一份树形依赖图

### 执行器
- 用于执行一切命令
- 执行器维护一份$PATH列表
    - 继承当前终端$PATH
    - 拦截所有软件执行
    > example:<br>
    > bash $ command<br>
    > 执行器接收命令command，由执行器查找并执行，跳过shell的查找过程
- 通过类哈希表O(1)查找
- 软件包通过chroot执行，绑定共享目录
- chroot附加内容见[拦截器](#拦截器)-1
- 共享目录见[拦截器](#拦截器)-对于软件包-读-以上规则不适用于公共目录

### 拦截器
- 拦截系统调用和文件操作，实现理论(基于chroot)详见[deepseek](https://chat.deepseek.com/share/sas0fpz3fo4ccbczpm)
- 定义
    - 系统目录：存在于主系统内(/)的目录
    - 软件目录：存在于当前软件chroot内的目录
- 对于软件包
    - 读
        - 读文件/目录在软件目录内存在 -> 直接读
        - 读文件/目录在软件目录不存在 -> 去系统目录读
        - 在系统目录不存在 -> 数据库搜
        - File / Directory Not Found
    - 创建文件/目录
        - 父目录是软件目录 -> 软件目录内创建
        - 父目录是系统目录 -> 系统目录内创建
        - 父目录是其他软件目录 -> 其他软件目录内创建
        - 以上规则不适用于公共目录
            - tempfs /tmp /srv /var /sys /proc /dev /media /mnt /lost+found
            - /root下非.目录
            - /home/*/下非.目录
    - 写
        - 文件在哪就写到哪
- 对于系统包
    - 读
        - 现在系统目录内读
        - 没有就去数据库读
        - File / Directory Not Found
    - 创建
        - 父目录在哪就创建到哪
        - 公共目录直接写系统目录
    - 写
        - 同上
- 所有文件更新同步到数据库

## 细节
### 管理器
#### 软件安装
##### 系统包安装
- 使用-s --system参数安装系统包
- 由pinarm调用apt进行安装
- pinarm在包信息数据库中记录包信息
- pinarm在依赖图中添加包

##### 软件包安装
- 当接收到多个安装请求时依次单独安装
> example:<br>
> sudo pinarm install app1 app2 app3<br>
> 先安装app1,再app2...
- 每个包的安装流程
    - 通过apt-get将deb包下载到~/.cache专用目录下
    - 解压下载的包到.cache专用目录下，目录名为包名
    - 检查md5sum
    - 读取control文件分析依赖
        - 检查是否有冲突，有冲突立即报错返回
        - 先通过本流程安装Pre-Depends
        - 再安装Depends
        - 然后安装Recommends
        - 显示建议包和增强包
    - 读取包信息，记录到包信息数据库
    - 查看安装的文件，记录到安装文件数据库
    - 记录依赖树
    - 复制解压好的包目录到/Applications
    - 复制动态链器
    - 使用lddtree为bin中可执行文件分析依赖，硬链接到指定位置
        - 在系统目录中查找
        - 在安装的依赖的文件数据库中查找
        - 报错
    - 使用执行器在chroot中执行postinst
    - 清理临时文件
    - 结束安装流程

#### 软件卸载
##### 系统包卸载
- 调用sudo apt purge --autoremove卸载
- 记录卸载的程序
- 在数据库中删除包信息
- 在依赖树中删除包记录
##### 软件包卸载
- chroot执行prerm remove
- chroot执行postrm purge
- 删除数据库中包信息
- 删除数据库中文件树
- 查找孤立地包计入autoremove列表
    - 在选择--autoremove时卸载
- 查找依赖的非孤立包分别执行prerm deconfigure

#### 数据库更新
- 执行sudo apt update
- 查找数据库中的包是否有新版本
- 标记
- 整合显示

#### 软件升级
##### 系统包
- 直接 sudo apt upgrade
- 更新包数据库
- 更新依赖数据库(如果需要)

##### 软件包
- 执行安装流程1-3
- 分析control文件
    - 查看是否有依赖变更
        - 减少依赖则查看该依赖是否孤立
            - 孤立则加入autoremove列表
        - 增加依赖则安装
        - 更新依赖树
    更新包数据库
- 复制并替换非etc文件
- 检查lddtree变更
- proot执行prerm upgrade 和postrm upgrade
- 更新文件数据库



