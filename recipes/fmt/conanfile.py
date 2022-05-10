from conans import ConanFile, MSBuild, tools
from shutil import copyfile
import os

class FmtConan(ConanFile):
    name = "fmt"
    license = "MIT"
    description = "{{fmt}} is an open-source formatting library providing a fast and safe alternative to C stdio and C++ iostreams."
    url = "https://fmt.dev/latest/index.html"

    # Settings and options
    settings = "os", "compiler", "arch", "build_type"

    options = { "fPIC": [True,False] }
    default_options = { "fPIC":True }

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/0.8.2@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    # Initialize the package
    def init(self):
        self.ice_init("cmake")
        self.build_requires = self._ice.build_requires

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    # Build both the debug and release builds
    def ice_build(self):
        definitions = { }
        definitions['FMT_INSTALL'] = False
        definitions['FMT_TEST'] = False
        definitions['FMT_DOC'] = False
        self.ice_run_cmake(definitions)

    def ice_package(self):
        self.copy("LICENSE.rst", src=self._ice.source_dir, dst="LICENSES")

        self.copy("*.h", "include", src="{}/include".format(self._ice.source_dir), keep_path=True)

        build_dir = self._ice.build_dir
        if self.settings.os == "Windows":
            self.copy("*.lib", "lib", build_dir, keep_path=False)
        if self.settings.os == "Linux":
            self.copy("*.a", "lib", build_dir, keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = ["lib"]
        if self.settings.build_type == "Release":
            self.cpp_info.libs = ["fmt"]
        else: # self.settings.build_type == "Debug":
            self.cpp_info.libs = ["fmtd"]
