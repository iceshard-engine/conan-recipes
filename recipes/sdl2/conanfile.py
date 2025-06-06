from conan import ConanFile
from conan.tools.files import get
from conan.tools.system.package_manager import Apt

class SDL2Conan(ConanFile):
    name = "sdl2"
    license = "Zlib"
    homepage = "https://www.libsdl.org/index.php"
    description = "Conan recipe for the SDL2 library."

    # Settings and options
    settings = "os", "compiler", "arch", "build_type"

    options = {
        "shared": [True, False],
        "sdl2main": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": True,
        "sdl2main": False,
        "fPIC": True
    }

    # Default user and channel values
    user = "iceshard"
    channel = "stable"

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/1.0.2@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    ice_generator = "cmake"
    ice_toolchain = "cmake"

    def system_requirements(self):
        # On linux systems we want to build SDL2 with Wayland support (all required packages)
        # apt = Apt(self)
        # We probably just want this as a warning
        # apt.install(["pkgconf", "libegl-dev", "libwayland-dev", "libxkbcommon-dev", "libxext-dev"], check=True)
        pass

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os == "Windows":
            if self.options.shared == False:
                self.output.warn("SDL2 cannot be build as Static library on Windows. Forcing Shared library build.")
            self.options.shared = True

    def package_id(self):
        self.info.options.sdl2main = "Any"

    def layout(self):
        if self.settings.os == "Windows":
            self.ice_layout("msbuild")
            self.folders.source = "sdl2-{}".format(self.version)
            self.folders.build = "sdl2-{}".format(self.version)
        else:
            self.ice_layout("cmake")

    def source(self):
        source_info = self.conan_data["sources"][self.ice_source_key(self.version)]
        get(self, **source_info, strip_root=True)

    def generate(self):
        if self.settings.os == "Windows":
            self.ice_generate("none", "msbuild")
        else:
            self.ice_generate()

    def ice_generate_cmake(self, tc, deps):
        tc.variables["CMAKE_C_COMPILER"] = str(self.settings.compiler)
        tc.variables["CMAKE_CXX_COMPILER"] = str(self.settings.compiler)

    # Build both the debug and release builds
    def ice_build(self):
        if self.settings.os == "Windows":
            self.ice_run_msbuild("VisualC/SDL.sln", retarget=True)
        else:
            self.ice_run_cmake()

    def ice_package_sources(self):
        self.ice_copy("COPYING.txt", src=".", dst="LICENSES") # (? before 2.0.22)
        self.ice_copy("LICENSE*", src=".", dst="LICENSES") # (starting from 2.0.22)
        self.ice_copy("*.h", src="include", dst="include", keep_path=True)
        # Copy config files later, because they will replace the default ones.
        self.ice_copy("SDL_config.h", src="{}/include".format(self.build_folder), dst="include", keep_path=False)

    def ice_package_artifacts(self):
        self.ice_copy("*.dll", src=".", dst="bin", keep_path=False)
        self.ice_copy("*.lib", src=".", dst="lib", keep_path=False)
        self.ice_copy("*.so*", src=".", dst="bin", keep_path=False)
        self.ice_copy("*.a", src=".", dst="lib", keep_path=False)

    def package_info(self):
        lib_suffix = "d" if self.settings.build_type == "Debug" else ""

        self.cpp_info.libs = []
        self.cpp_info.libdirs = [ 'lib' ]
        self.cpp_info.bindirs = [ 'bin' ]
        self.cpp_info.includedirs = [ 'include' ]

        if self.settings.os == "Windows":
            self.cpp_info.libs = ['SDL2']

            if self.options.sdl2main == True:
                self.cpp_info.libs.append("SDL2main")

        if self.settings.os == "Linux":
            self.cpp_info.libdirs.append("bin")

            if self.options.shared:
                self.cpp_info.libs = [ 'SDL2-2.0' + lib_suffix ]
            else:
                self.cpp_info.libs = [ 'SDL2' + lib_suffix ]

            if self.options.sdl2main == True:
                self.cpp_info.libs.append('SDL2main' + lib_suffix)
