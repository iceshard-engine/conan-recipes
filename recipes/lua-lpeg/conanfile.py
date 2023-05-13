from conan import ConanFile
from conan.tools.files import copy
import os

class LuaLpegConan(ConanFile):
    name = "lua-lpeg"
    license = "MIT"
    description = "LPeg is a pattern-matching library for Lua, based on Parsing Expression Grammars (PEGs)."
    url = "https://github.com/LuaDist/lpeg"

    settings = "os", "build_type", "compiler", "arch"

    options = { "shared": [True, False] }
    default_options = { "shared":True }

    exports_sources = ["premake5.lua", "LICENSE_LPEG.txt"]
    requires = "lua/5.1.5@iceshard/stable"

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/0.9.0@iceshard/stable", "premake-generator/0.2.0@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    ice_generator = "premake5"
    ice_toolchain = "native"

    def source(self):
        self.ice_source()
        copy(self, "premake5.lua", src=self.export_sources_folder, dst=self.source_folder)

    def ice_build(self):
        if self.settings.compiler == "msvc":
            self.ice_run_msbuild("LuaLPeg.sln")
        else:
            self.ice_run_make()

    def ice_package_sources(self):
        self.ice_copy("LICENSE_LPEG.txt", src=self.export_sources_folder, dst="LICENSES")
        self.ice_copy("*.h", src=".", dst="include", keep_path=False)

    def ice_package_artifacts(self):
        self.ice_copy("*.lib", src=".", dst="lib", keep_path=False)
        self.ice_copy("*.dll", src=".", dst="bin", keep_path=False)
        self.ice_copy("*.a", src=".", dst="lib", keep_path=False)
        self.ice_copy("*.so", src=".", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = [ "lib" ]
        self.cpp_info.includedirs = [ "include" ]
        self.cpp_info.libs = [ "lpeg" ]

        # Enviroment info
        if self.settings.os == "Windows":
            self.runenv_info.append_path("LUA_CPATH", os.path.join(self.package_folder, "bin/?.dll"))
        if self.settings.os == "Linux":
            self.runenv_info.append_path("LUA_CPATH", os.path.join(self.package_folder, "lib/lib?.so"))
