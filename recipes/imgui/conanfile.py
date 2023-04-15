from conan import ConanFile
from conan.tools.files import rm, rmdir, copy

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
    python_requires = "conan-iceshard-tools/0.9.0@iceshard/stable", "premake-generator/0.2.0@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    ice_generator = "premake5"
    ice_toolchain = "native"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def generate(self):
        copy(self, "premake5.lua", src=self.export_sources_folder, dst=self.source_folder)
        # Switch to the docking branch before continuing
        if self.options.docking_branch:
            self.run("git checkout docking")
        self.ice_generate()

    def ice_build(self):
        if self.settings.compiler == "msvc":
            self.ice_run_msbuild("imgui.sln")
        else:
            self.ice_run_make()

    def ice_package_sources(self):
        self.ice_copy("LICENSE.txt", src=".", dst="LICENSES")
        self.ice_copy("*.h", src=".", dst="include/imgui", keep_path=True, excludes=("examples/*", "misc/*"))

    def ice_package_artifacts(self):
        self.ice_copy("*.lib", dst="lib", src="bin", keep_path=False)
        self.ice_copy("*.a", dst="lib", src="bin", keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = [ "lib" ]
        self.cpp_info.libs = [ "imgui" ]
