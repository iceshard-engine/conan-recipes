from conan import ConanFile

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

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/0.9.0@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    ice_generator = "cmake"
    ice_toolchain = "cmake"

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
            self.folders.source = "."
            self.folders.build = "SDL2-{}".format(self.version)
        else:
            self.ice_layout("cmake")

    def generate(self):
        if self.settings.os == "Windows":
            self.ice_generate("none", "msbuild")
        else:
            self.ice_generate()

    # Build both the debug and release builds
    def ice_build(self):
        if self.settings.os == "Windows":
            self.ice_run_msbuild("VisualC/SDL.sln", retarget=True)
        else:
            self.ice_run_cmake()

    def ice_package_sources(self):
        self.ice_copy("COPYING.txt", src=self.build_folder, dst="LICENSES") # (? before 2.0.22)
        self.ice_copy("LICENSE.txt", src=self.build_folder, dst="LICENSES") # (starting from 2.0.22)
        self.ice_copy("*.h", src="{}/include".format(self.build_folder), dst="include", keep_path=False)

    def ice_package_artifacts(self):
        self.ice_copy("*SDL2.dll", src=".", dst="bin", keep_path=False)
        self.ice_copy("*SDL2.lib", src=".", dst="lib", keep_path=False)
        self.ice_copy("*SDL2main.lib", src=".", dst="lib", keep_path=False)

        self.ice_copy("libSDL2-2.0[d].so*", src=".", dst="bin", keep_path=False)
        self.ice_copy("libSDL2main[d].a", src=".", dst="lib", keep_path=False)
        self.ice_copy("libSDL2[d].a", src=".", dst="lib", keep_path=False)

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ['SDL2']
            self.cpp_info.libdirs = ['lib']
            self.cpp_info.bindirs = ['bin']
            self.cpp_info.includedirs = ["include"]

            if self.options.sdl2main == True:
                self.cpp_info.libs.append("SDL2main")

        if self.settings.os == "Linux":
            self.cpp_info.libdirs = ['lib']

            if self.options.shared:
                self.cpp_info.bindirs = ['bin']
                self.cpp_info.libdirs.append("bin")
                if self.settings.build_type == "Debug":
                    self.cpp_info.libs = ['SDL2-2.0d']
                else:
                    self.cpp_info.libs = ['SDL2-2.0']
            else:
                if self.settings.build_type == "Debug":
                    self.cpp_info.libs = ['SDL2d']
                else:
                    self.cpp_info.libs = ['SDL2']

            if self.options.sdl2main == True:
                if self.settings.build_type == "Debug":
                    self.cpp_info.libs = ['SDL2maind']
                else:
                    self.cpp_info.libs = ['SDL2main']
