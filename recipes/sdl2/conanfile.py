from conans import ConanFile, MSBuild, CMake, tools
import shutil
import os

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

    source_dir = "SDL2-{version}"

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/0.8.2@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    # Initialize the package
    def init(self):
        self.ice_init("cmake")
        self.build_requires = self._ice.build_requires

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os == "Windows":
            if self.options.shared == False:
                self.output.warn("SDL2 cannot be build as Static library on Windows. Forcing Shared library build.")
            self.options.shared = True

    # Update the package id
    def package_id(self):
        self.info.options.sdl2main = "Any"

    # Build both the debug and release builds
    def ice_build(self):
        if self.settings.compiler == "Visual Studio":
            self.ice_run_msbuild("VisualC/SDL.sln")

        else:
            self.ice_run_cmake()

    def ice_package(self):
        # Copy the license file (before 2.0.22)
        self.copy("COPYING.txt", src=self._ice.source_dir, dst="LICENSES")
        # Copy the license file (around 2.0.22)
        self.copy("LICENSE.txt", src=self._ice.source_dir, dst="LICENSES")

        self.copy("*.h", "include", "{}/include".format(self._ice.source_dir), keep_path=False)

        build_dir = self._ice.build_dir
        if self.settings.compiler == "Visual Studio":
            build_dir = os.path.join(self._ice.source_dir, "VisualC/x64/{}".format(self.settings.build_type))

        if self.settings.os == "Windows":
            self.copy("SDL2.dll", dst="bin", src=build_dir, keep_path=False)
            self.copy("SDL2.pdb", dst="bin", src=build_dir, keep_path=False)
            self.copy("SDL2.lib", dst="lib", src=build_dir, keep_path=False)
            self.copy("SDL2main.lib", dst="lib", src=build_dir, keep_path=False)

        if self.settings.os == "Linux":
            if self.options.shared == True:
                if self.settings.build_type == "Debug":
                    self.copy("libSDL2-2.0d.so*", dst="bin", src=build_dir, keep_path=False)
                    self.copy("libSDL2maind.a", dst="lib", src=build_dir, keep_path=False)
                else:
                    self.copy("libSDL2-2.0.so*", dst="bin", src=build_dir, keep_path=False)
                    self.copy("libSDL2main.a", dst="lib", src=build_dir, keep_path=False)
            else:
                if self.settings.build_type == "Debug":
                    self.copy("libSDL2d.a", dst="lib", src=build_dir, keep_path=False)
                    self.copy("libSDL2maind.a", dst="lib", src=build_dir, keep_path=False)
                else:
                    self.copy("libSDL2.a", dst="lib", src=build_dir, keep_path=False)
                    self.copy("libSDL2main.a", dst="lib", src=build_dir, keep_path=False)


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
