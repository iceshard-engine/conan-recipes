from conans import ConanFile, MSBuild, tools
from shutil import copyfile
import os

class LuaConan(ConanFile):
    name = "lua"
    license = "MIT"
    description = "Lua conan package"
    url = "https://www.lua.org/home.html"

    settings = "os", "build_type", "compiler", "arch"

    options = { "shared": [True, False] }
    default_options = { "shared":True }

    exports_sources = ["premake5.lua"]

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/0.8.2@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"


    def init(self):
        self.ice_init("premake5")
        self.build_requires = self._ice.build_requires

    def ice_build(self):
        self.ice_generate()
        if self.settings.compiler == "Visual Studio":
            self.ice_run_msbuild("Lua.sln", self.settings.build_type)

        else:
            self.ice_run_make(self.settings.build_type)

    def ice_package(self):

        self.copy("COPYRIGHT", src=self._ice.source_dir, dst="LICENSE")

        self.copy("*.hpp", "include", src="{}/etc".format(self._ice.source_dir), keep_path=False)
        for include in ["lua.h", "lualib.h", "lauxlib.h", "luaconf.h"]:
            self.copy(include, "include", src="{}/src".format(self._ice.source_dir), keep_path=False)

        build_dir = os.path.join(self._ice.build_dir, "bin")
        if self.settings.os == "Windows":
            self.copy("*.exe", "bin", build_dir, keep_path=False)
            self.copy("*.lib", "lib", build_dir, keep_path=False)
            if self.options.shared:
                self.copy("*.dll", "bin", build_dir, keep_path=False)
        if self.settings.os == "Linux":
            self.copy("*/lua", "bin", build_dir, keep_path=False)
            self.copy("*/luac", "bin", build_dir, keep_path=False)

            self.copy("*.a", "lib", build_dir, keep_path=False)
            if self.options.shared:
                self.copy("*.so", "lib", build_dir, keep_path=False)


    def package_info(self):
        self.cpp_info.bindirs = [ "bin" ]
        self.cpp_info.libdirs = [ "lib" ]
        self.cpp_info.libs = [ "lua51" ]

        # Enviroment info
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        if self.settings.os == "Linux":
            self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
