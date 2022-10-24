from conans import ConanFile, MSBuild, tools
from shutil import copyfile
import os

class ImGuiConan(ConanFile):
    name = "imgui"
    license = "https://github.com/ocornut/imgui/blob/master/LICENSE.txt"
    description = "Dear ImGui: Bloat-free Immediate Mode Graphical User interface for C++ with minimal dependencies"
    url = "https://github.com/ocornut/imgui"

    # Setting and options
    settings = "os", "compiler", "arch", "build_type"
    options = { "docking_branch":[True, False], "fPIC":[True, False] }
    default_options = { "docking_branch":False, "fPIC":True }

    # Additional files to export
    exports_sources = ["premake5.lua"]

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/0.8.2@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    def init(self):
        self.ice_init("premake5")
        self.build_requires = self._ice.build_requires

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    # Extend source selection key generation
    def ice_source_key(self, version):
        if self.options.docking_branch == True:
            return "{}-docking".format(version)
        else:
            return version

    # Build both the debug and release builds
    def ice_build(self):
        self.ice_generate()

        if self.settings.compiler == "Visual Studio":
            self.ice_run_msbuild("imgui.sln")
        else:
            self.ice_run_make()

    def package(self):
        self.copy("LICENSE.txt", src=self._ice.source_dir, dst="LICENSE")
        self.copy("*.h", "include/imgui", src=self._ice.source_dir, keep_path=True, excludes=("examples/*", "misc/*"))

        build_bin_dir = os.path.join(self._ice.build_dir, "bin")
        if self.settings.os == "Windows":
            self.copy("*.lib", dst="lib", src=build_bin_dir, keep_path=False)
        if self.settings.os == "Linux":
            self.copy("*.a", dst="lib", src=build_bin_dir, keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = [ "lib" ]
        self.cpp_info.libs = [ "imgui" ]
