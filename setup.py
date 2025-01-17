#!/usr/bin/env python
# flake8: noqa
from os import path
from shutil import copyfile
from pathlib import Path
from subprocess import check_call
from typing import Optional, List, Dict
from setuptools import setup, Command
from setuptools.command.build import build, SubCommand
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools.command.install import install as _install


build.sub_commands.insert(0, ("compile_uap_cpp", None))


class CustomInstallCommand(_install):
    def run(self):
        _install.run(self)

        # после установки копируем файл regexes.yaml
        source_file = Path('uap-core/regexes.yaml')
        target_file = Path(self.install_lib, 'ua_parser/regexes.yaml')
        if source_file.is_file():
            copyfile(source_file, target_file)


class CompileUapCpp(Command, SubCommand):
    def initialize_options(self) -> None:
        self.pkg_name: Optional[str] = None

    def finalize_options(self) -> None:
        self.pkg_name = self.distribution.get_name().replace("-", "_")

    def get_source_files(self) -> List[str]:
        return ["uap-cpp/libuaparser_cpp.a"]

    def get_outputs(self) -> List[str]:
        return [f"{self.pkg_name}/libuaparser_cpp.a"]

    def get_output_mapping(self) -> Dict[str, str]:
        return dict(zip(self.get_source_files(), self.get_outputs()))

    def run(self) -> None:
        if not path.exists('uap-cpp/libuaparser_cpp.a'):
            check_call(['make', 'uaparser_cpp'], cwd='uap-cpp')


ext_modules = [
    Pybind11Extension(
        "ua_parser.pyuapcpp",
        ["src/main.cpp"],
        include_dirs=['uap-cpp'],
        extra_compile_args=["-std=c++14"],
        extra_objects=['uap-cpp/libuaparser_cpp.a'],
        extra_link_args=['uap-cpp/libuaparser_cpp.a', '-lre2', '-lyaml-cpp'],
    ),
]

setup(
    cmdclass={
        "install": CustomInstallCommand,
        "compile_uap_cpp": CompileUapCpp,
        "build_ext": build_ext
    },
    include_package_data=True,
    ext_modules=ext_modules,
    zip_safe=False
)
