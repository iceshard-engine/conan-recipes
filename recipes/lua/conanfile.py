from conan import ConanFile
from conan.tools.system.package_manager import Apt
from conan.tools.microsoft import NMakeToolchain
from conan.tools.files import chdir, replace_in_file
import os

class LuaConan(ConanFile):
    name = "lua"
    license = "MIT"
    description = "Lua is a powerful, efficient, lightweight, embeddable scripting language."
    url = "https://www.lua.org/home.html"

    settings = "os", "build_type", "compiler", "arch"

    options = { "shared": [True, False] }
    default_options = { "shared":True }

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/1.0.2@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    ice_generator = "none" # "premake5"
    ice_toolchain = "makefile"

    # def system_requirements(self):
    #     Apt(self).install(["libreadline-dev"], check=True) # Just check and install if necessary

    def layout(self):
        self.ice_layout("none")
        self.folders.source = "."
        self.folders.build = "lua-{}".format(self.version)

    def generate(self):
        tc = NMakeToolchain(self)
        tc.generate()

        chdir(self, self.source_folder)
        replace_in_file(self, os.path.join(self.source_folder, "lua-{}/src/Makefile".format(self.version)), "-Wall $(MYCFLAGS)", "-Wall -fPIC $(MYCFLAGS)")

    def ice_build(self):
        if self.settings.compiler == 'msvc':
            self.run("etc\\luavs.bat")
        elif self.settings.os == "Linux":
            self.run("make linux")
        elif self.settings.os == "Macos":
            self.run("make macosx")

    def ice_package_sources(self):
        self.ice_copy("COPYRIGHT", src=".", dst="LICENSE")
        self.ice_copy("*/etc/*.hpp", src=".", dst="include", keep_path=False)
        for include in ["*/src/lua.h", "*/src/lualib.h", "*/src/lauxlib.h", "*/src/luaconf.h"]:
            self.ice_copy(include, src=".", dst="include", keep_path=False)

    def ice_package_artifacts(self):
        self.ice_copy("*.exe", src=".", dst="bin", keep_path=False)
        self.ice_copy("*.lib", src=".", dst="lib", keep_path=False)
        self.ice_copy("*.dll", src=".", dst="bin", keep_path=False)

        self.ice_copy("*/lua", src=".", dst="bin", keep_path=False)
        self.ice_copy("*/luac", src=".", dst="bin", keep_path=False)
        self.ice_copy("*.a", src=".", dst="lib", keep_path=False)
        self.ice_copy("*.so", src=".", dst="bin", keep_path=False)

    def package_info(self):
        self.cpp_info.includedirs = [ "include" ]
        self.cpp_info.bindirs = [ "bin" ]
        self.cpp_info.libdirs = [ "lib" ]

        if self.settings.os == "Windows":
            self.cpp_info.libs = [ "lua51" ]
        else:
            self.cpp_info.libs = [ "lua" ]

        # CMake info
        self.cpp_info.set_property("cmake_file_name", "lua")
        self.cpp_info.set_property("cmake_target_name", "lua")

        # Enviroment info
        self.runenv_info.append_path("PATH", os.path.join(self.package_folder, "bin"))
        self.buildenv_info.append_path("CMAKE_PROGRAM_PATH", os.path.join(self.package_folder, "bin"))
        if self.settings.os == "Linux" or self.settings.os == "Macos":
            self.buildenv_info.append_path("LD_LIBRARY_PATH", os.path.join(self.package_folder, "bin"))
