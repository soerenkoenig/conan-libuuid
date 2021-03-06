#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration


class LibuuidConan(ConanFile):
    name = "libuuid"
    version = "1.0.3"
    description = "Portable uuid C library"
    url = "https://github.com/bincrafters/conan-libuuid"
    homepage = "https://sourceforge.net/projects/libuuid/"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "BSD-3-Clause"
    topics = ("conan", "libuuid", "uuid", "unique-id", "unique-identifier")
    exports = ["LICENSE.md"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _source_subfolder = "source_subfolder"
    _autotools = None

    def source(self):
        source_url = "https://downloads.sourceforge.net/project/libuuid"
        tools.get("{}/{}-{}.tar.gz".format(source_url, self.name, self.version),
                  sha256="46af3275291091009ad7f1b899de3d0cea0252737550e7919d17237997db5644")
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def configure(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("libuuid is not supported on Windows")
        del self.settings.compiler.libcxx

    def _configure_autotools(self):
        if not self._autotools:
            configure_args = [
                "--enable-shared=%s" % ("yes" if self.options.shared else "no"),
                "--enable-static=%s" % ("no" if self.options.shared else "yes")
                ]
            self._autotools = AutoToolsBuildEnvironment(self)
            if "x86" in self.settings.arch:
                self._autotools.flags.append('-mstackrealign')
            self._autotools.configure(args=configure_args)
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()
        la = os.path.join(self.package_folder, "lib", "libuuid.la")
        if os.path.isfile(la):
            os.unlink(la)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "uuid"))
