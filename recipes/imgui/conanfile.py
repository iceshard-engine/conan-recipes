from conan import ConanFile
from conan.tools.files import copy, rename
from os.path import join

class ImGuiConan(ConanFile):
    name = "imgui"
    license = "https://github.com/ocornut/imgui/blob/master/LICENSE.txt"
    description = "Dear ImGui: Bloat-free Immediate Mode Graphical User interface for C++ with minimal dependencies"
    url = "https://github.com/ocornut/imgui"

    # Setting and options
    settings = "os", "compiler", "arch", "build_type"
    options = { "fPIC":[True, False] }
    default_options = { "fPIC":True }

    # Additional files to export
    exports_sources = ["CMakeLists.txt", "CMakeLists.docking.txt"]

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/1.0.0@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    ice_generator = "cmake"
    ice_toolchain = "ninja"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        # Get the selected sources
        self.ice_source()

        # Select the file we want to move to the source location
        type_clists = ".docking" if "docking" in self.version else ""

        src_clists = join(self.export_sources_folder, "CMakeLists{}.txt".format(type_clists))
        dst_clists = join(self.source_folder, "CMakeLists.txt")

        # Move the CMakeLists.txt file
        rename(self, src=src_clists, dst=dst_clists)

    def ice_build(self):
        variables = { }
        if self.settings.os != "Windows":
            variables['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        self.ice_run_cmake(variables)

    def ice_package_sources(self):
        self.ice_copy("LICENSE.txt", src=".", dst="LICENSES")
        self.ice_copy("*.h", src=".", dst="include/imgui", keep_path=True, excludes=("examples/*", "misc/*"))

    def ice_package_artifacts(self):
        self.ice_copy("*.lib", dst="lib", src=".", keep_path=False)
        self.ice_copy("*.a", dst="lib", src=".", keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = [ "lib" ]
        self.cpp_info.libs = [ "imgui" ]
