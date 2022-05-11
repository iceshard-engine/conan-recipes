from conans import ConanFile, MSBuild, tools
from shutil import copyfile
import os

class TracyConan(ConanFile):
    name = "tracy"
    license = "BSD-3-Clause"
    description = "A real time, nanosecond resolution, remote telemetry, hybrid frame and sampling profiler for games and other applications."
    url = "https://github.com/wolfpld/tracy"

    # Settings and options
    settings = "os", "compiler", "arch", "build_type"
    options = { "shared":[True, False], "tracy_fibers":[True, False] }
    default_options = { "shared":True, "tracy_fibers":False }

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/0.8.2@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    # Initialize the package
    def init(self):
        self.ice_init("cmake")
        self.build_requires = self._ice.build_requires

    # Build both the debug and release builds
    def ice_build(self):
        definitions = { }
        definitions['TRACY_FIBERS'] = self.options.tracy_fibers
        self.ice_run_cmake(definitions)

    def ice_package(self):
        self.copy("LICENSE", src=self._ice.source_dir, dst="LICENSES/")

        self.copy("*.h*", "include/tracy/common", src="{}/common".format(self._ice.source_dir), keep_path=True)
        self.copy("*.h*", "include/tracy/client", src="{}/client".format(self._ice.source_dir), keep_path=True)
        self.copy("Tracy*.hpp", "include/tracy", src="{}".format(self._ice.source_dir), keep_path=True)
        self.copy("Tracy*.h", "include/tracy", src="{}".format(self._ice.source_dir), keep_path=True)

        build_dir = self._ice.build_dir

        if self.settings.os == "Windows":
            build_dir = os.path.join(build_dir, str(self.settings.build_type))

            self.copy("*.lib", dst="lib", src=build_dir, keep_path=False)
            if self.options.shared:
                self.copy("*.dll", dst="bin", src=build_dir, keep_path=False)
                self.copy("*.pdb", dst="bin", src=build_dir, keep_path=False)
            else:
                self.copy("*.pdb", dst="lib", src=build_dir, keep_path=False)
        if self.settings.os == "Linux":
            if self.options.shared:
                self.copy("*.so", dst="bin", src=build_dir, keep_path=False)
            else:
                self.copy("*.a", dst="lib", src=build_dir, keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = ['lib']
        self.cpp_info.libs = ['TracyClient']

        if self.options.tracy_fibers:
            self.cpp_info.defines = ['TRACY_FIBERS']

        if self.options.shared:
            self.cpp_info.bindirs = ['bin']

            if self.settings.os == 'Linux':
                self.cpp_info.libdirs.append('bin')
