#!/usr/bin/env python3
import argparse
import subprocess
# import logger
import sys

from pathlib import Path

HOME = Path.home()

def install(args: argparse.Namespace):
    ASK = True
    DRYRUN = False
    if args.yes:
        ASK = False
    elif args.dry_run:
        DRYRUN = True
    # log(f"Install {args.package} with {ASK =}, {DRYRUN =}")

    # 下载deb
    for package in args.package:
        download = subprocess.run(["sudo", "apt-get", "install", "--reinstall", \
                        "--download-only", "-y", package,\
                        "-o", f"Dir::Cache::archives=\"{HOME / '.pinarm' / 'cache' / 'archives'}\""],
                        capture_output=True, text=True)
        if not download.returncode:
            # log(f"Downloaded {package} successfully \n {download.stdout}")
            ...
        else:
            # log(f"Failed to download {package} \n {download.stderr}")
            print(f"Failed to download {package}, apt exited with code {download.returncode}")
            sys.exit(1)
    # 列出下载的deb文件
    deb_files = list((HOME / '.pinarm' / 'cache' / 'archives').glob("*.deb"))
    print(f"Downloaded {len(deb_files)} deb file(s):")
    # log(f"Downloaded {len(deb_files)} deb file(s):")
    for f in deb_files:
        print(f"  {f.name}", end="")
    do_install = input("install?[Y/n]")
    # log(f"User input: {do_install}")
    if do_install.lower() in ["y", "", "yes"]:
        # 解压
        for f in deb_files:
            unpack = subprocess.run(["dpkg-deb", "-R", f.name, f"{HOME / '.pinarm' / 'cache' / 'unpacked'/ f.stem}"], capture_output=True, text=True)
            if not unpack.returncod:
                # log(f"Unpacked {f.name}\n{unpack.stdout}")
                print(f"Unpacked {f.name}")
            else:
                # log(f"Failed to unpack {f.name}\n{unpack.stderr}")
                print(f"Failed to unpack {f.name}, dpkg-deb exited with code {unpack.returncode}")
                exit(1)
    else:
        print("Aborted.")
        # log("exit.")
        sys.exit(0)
    # 创建安装目录
    unpacked_dirs = [d for d in (HOME / '.pinarm' / 'cache' / 'unpacked').iterdir() if d.is_dir()]
    # log(f"Unpacked directories: {unpacked_dirs}")
    for d in unpacked_dirs:
        # 读取control文件
        ...


        
            
    


def remove(args):
    ... 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pinarm package manage: the package manager for HYOS to manage user packages")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # install command
    parser_install = subparsers.add_parser("install", help="Install a package")
    parser_install.add_argument("package", nargs="+", help="Package name(s) to install")
    parser_install.add_argument("-y", "--yes", help="Automatically answer yes to prompts")
    parser_install.add_argument("--dry-run", help="Show what would be done without actually doing it")

    # remove command
    parser_remove = subparsers.add_parser("remove", help="Remove a package")
    parser_remove.add_argument("package", nargs="+", help="Package name(s) to remove")

    # update command
    parser_update = subparsers.add_parser("update", help="Update package list")
    parser_update.add_argument("package", nargs="*", help="Package name(s) to update")

    # search command
    parser_search = subparsers.add_parser("search", help="Search for a package")
    parser_search.add_argument("query", help="Search query")

    # list command
    parser_list = subparsers.add_parser("list", help="List installed packages")
    # parser_list.add_argument("-a", "--all", action="store_true", help="List all available packages")

    args = parser.parse_args()

    if args.command == "install":
        install(args)
    elif args.command == "remove":
        remove(args)
    else:
        print("暂不支持")

