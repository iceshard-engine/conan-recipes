from conan import ConanFile
from conan.tools.files import replace_in_file
import os

class Box2DConan(ConanFile):
    name = "box2d"
    license = "MIT"
    description = "Box2D is a 2D physics engine for games."
    url = "https://github.com/erincatto/box2d"

    # Default version, channel and user
    version_default = "3.0.0"
    channel = "stable"
    user = "iceshard"

    # Settings and options
    settings = "os", "compiler", "arch", "build_type"

    options = { "shared":[True, False], "fPIC":[True,False], "profiled":[True,False], "validated":[True,False] }
    default_options = { "shared":False, "fPIC":True, "profiled":False, "validated":False }

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/1.0.2@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    ice_generator = "cmake"
    ice_toolchain = "ninja"

    def set_version(self):
        self.version = self.version or self.version_default

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def ice_generate_cmake(self, tc, deps):
        super().ice_generate_cmake(tc, deps)

        # For Emscripten we need to ensure we are compiled with -pthread and -sSHARED_MEMORY support
        if self.settings.os == "Emscripten":
            main_cmake = os.path.join(self.source_folder, "src", "CMakeLists.txt")
            replace_in_file(self, main_cmake, "-msimd128 -msse2", "-msimd128 -msse2 -pthread -sSHARED_MEMORY=1")

    def ice_build(self):
        variables = { }

        # Box2D specific
        variables['BOX2D_SAMPLES'] = False
        variables['BOX2D_UNIT_TESTS'] = False
        variables['BOX2D_PROFILE'] = self.options.profiled
        variables['BOX2D_VALIDATE'] = self.options.validated

        # We don't want to install anything
        if self.settings.os != "Windows":
            variables['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        self.ice_run_cmake(variables=variables)

    def ice_package_sources(self):
        self.ice_copy("LICENSE", src=".", dst="LICENSES")
        self.ice_copy("*.h", src="include", dst="include", keep_path=True)

    def ice_package_artifacts(self):
        self.ice_copy("*.lib", src=".", dst="lib", keep_path=False)
        self.ice_copy("*.dll", src=".", dst="bin", keep_path=False)
        self.ice_copy("*.a", src=".", dst="lib", keep_path=False)
        self.ice_copy("*.so*", src=".", dst="bin", keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = ["lib"]
        if self.settings.os != "Windows":
            self.cpp_info.libdirs.append("bin")

        if self.settings.build_type == "Debug":
            self.cpp_info.libs = ["box2dd"]
        else:
            self.cpp_info.libs = ["box2d"]
