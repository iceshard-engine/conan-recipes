from conans import ConanFile, MSBuild, tools
from shutil import copyfile
import os

class Chipmunk2DConan(ConanFile):
    name = "chipmunk2d"
    license = "MIT"
    description = "A fast and lightweight 2D game physics library."
    url = "https://github.com/slembcke/Chipmunk2D"

    # Settings and options
    settings = "os", "compiler", "arch", "build_type"

    options = { "shared":[True, False], "fPIC":[True,False] }
    default_options = { "shared":False, "fPIC":True }

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
        definitions['BUILD_DEMOS'] = False
        definitions['BUILD_SHARED'] = self.options.shared
        definitions['BUILD_STATIC'] = not self.options.shared

        # We don't want to install anything
        definitions['INSTALL_DEMOS'] = False
        definitions['INSTALL_STATIC'] = False
        if self.settings.os != "Windows":
            definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        self.ice_run_cmake(definitions)

    def ice_package(self):
        self.copy("LICENSE.txt", src=self._ice.source_dir, dst="LICENSES")

        self.copy("*.h", "include", src="{}/include".format(self._ice.source_dir), keep_path=True)

        build_dir = self._ice.build_dir
        if self.settings.os == "Windows":
            self.copy("*.lib", "lib", build_dir, keep_path=False)
            self.copy("*.dll", "bin", build_dir, keep_path=False)
        if self.settings.os == "Linux":
            self.copy("*.a", "lib", build_dir, keep_path=False)
            self.copy("*.so*", "bin", build_dir, keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = ["lib"]
        if self.settings.os == "Linux":
            self.cpp_info.libdirs.append("bin")

        self.cpp_info.libs = ["chipmunk"]
