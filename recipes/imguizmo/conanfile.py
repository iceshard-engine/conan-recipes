from conan import ConanFile
from conan.tools.files import copy, rename, replace_in_file
from os.path import join

class ImGuizmoConan(ConanFile):
    name = "imguizmo"
    license = "https://github.com/CedricGuillemet/ImGuizmo?tab=MIT-1-ov-file#readme"
    description = "Immediate mode 3D gizmo for scene editing and other controls based on Dear Imgui"
    url = "https://github.com/CedricGuillemet/ImGuizmo"

    # Default values for version, user and channel
    version_default = "1.91.5"
    user = "iceshard"
    channel = "stable"

    # Setting and options
    settings = "os", "compiler", "arch", "build_type"
    options = { "fPIC":[True, False] }
    default_options = { "fPIC":True }

    # Additional files to export
    exports_sources = ["CMakeLists.txt", "patches/*"]

    # Iceshard conan tools
    requires = "imgui/[>=1.90]@iceshard/stable"
    python_requires = "conan-iceshard-tools/1.0.1@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    ice_generator = "cmake"
    ice_toolchain = "ninja"

    def set_version(self):
        self.version = self.version or self.version_default

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        # Get the selected sources
        self.ice_source()

        src_clists = join(self.export_sources_folder, "CMakeLists.txt")
        dst_clists = join(self.source_folder, "CMakeLists.txt")

        # Move the CMakeLists.txt file
        rename(self, src=src_clists, dst=dst_clists)

    def ice_build(self):
        variables = { }
        if self.settings.os != "Windows":
            variables['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        self.ice_run_cmake(variables)

    def ice_package_sources(self):
        self.ice_copy("LICENSE", src=".", dst="LICENSES")
        self.ice_copy("ImGuizmo.h", src=".", dst="include/imguizmo", keep_path=True, excludes=("examples/*", "misc/*"))

    def ice_package_artifacts(self):
        self.ice_copy("*.lib", dst="lib", src=".", keep_path=False)
        self.ice_copy("*.a", dst="lib", src=".", keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = [ "lib" ]
        self.cpp_info.libs = [ "imguizmo" ]
