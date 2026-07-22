# pinarm

## 安装
1. 下载deb
2. 解压
3. 读control
> Package: <包名>                        # 必须
> Version: <版本号>                      # 必须
> Architecture: <架构>                   # 必须
> Maintainer: <维护者>                   # 必须
> Description: <简短描述>                # 必须
>  <长描述>                              # 必须（每行以空格开头）
>
> Installed-Size: <整数>                 # 可选，安装后大小（KB）
> Essential: yes                         # 可选，是否为系统核心包
> Priority: <优先级>                     # 可选（required/important/standard/optional/extra）
> Section: <分类>                        # 可选（admin/utils/net/libs/devel等）
> 
> Depends: <包名> (>= <版本>), ...       # 可选，必须的依赖
> Pre-Depends: <包名>, ...               # 可选，安装前必须配置好的依赖
> Recommends: <包名>, ...                # 可选，推荐安装
> Suggests: <包名>, ...                  # 可选，建议安装
> Enhances: <包名>, ...                  # 可选，增强的包
> Breaks: <包名> (<< <版本>), ...        # 可选，破坏的包
> Conflicts: <包名>, ...                 # 可选，冲突的包
> Replaces: <包名>, ...                  # 可选，替代的包
> Provides: <虚拟包名>, ...              # 可选，提供的虚拟包
> 
> Homepage: <URL>                        # 可选，项目主页
> Multi-Arch: <值>                       # 可选（same/foreign/allowed）
> Built-Using: <包名> (= <版本>), ...    # 可选，构建时使用的包
> Source: <源码包名>                     # 可选，源码包名
 - 转成Dict
 - 需要: Depends, Pre-Depends, Recommends
 - 递归安装: 先装Pre-Depends, 再装Depends,再装本体，最后装Recommends
4. 安装：
 - 去数据库检查是否已经安装
