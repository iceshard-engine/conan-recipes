from conan import ConanFile

class TracyConan(ConanFile):
    name = "tracy"
    license = "BSD-3-Clause"
    description = "A real time, nanosecond resolution, remote telemetry, hybrid frame and sampling profiler for games and other applications."
    url = "https://github.com/wolfpld/tracy"

    # Default values for version, user and channel
    version_default = "0.11.1"
    user = "iceshard"
    channel = "stable"

    # Settings and options
    settings = "os", "compiler", "arch", "build_type"
    options = {
        "shared":[True, False],
        "fibers":[True, False],
        "manual_lifetime":[True, False],
        "no_system_tracing":[True, False],
        "no_sampling":[True, False]
    }
    default_options = {
        "shared":True,
        "fibers":False,
        "manual_lifetime":False,
        "no_system_tracing":False,
        "no_sampling":False
    }

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/0.9.1@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    # ICT Specific fields
    ice_generator = "cmake"
    ice_toolchain = "ninja"

    def set_version(self):
        self.version = self.version or self.version_default

    def ice_generate_cmake(self, toolchain, deps):
        toolchain.variables['TRACY_FIBERS'] = self.options.fibers
        toolchain.variables['TRACY_MANUAL_LIFETIME'] = self.options.manual_lifetime
        toolchain.variables['TRACY_DELAYED_INIT'] = self.options.manual_lifetime
        toolchain.variables['TRACY_NO_SYSTEM_TRACING'] = self.options.no_system_tracing
        toolchain.variables['TRACY_NO_SAMPLING'] = self.options.no_sampling

        # # For EmScripten we build with -pthread support and shared memory
        # if self.settings.os == "Emscripten":
        #     toolchain.extra_cxxflags = ['-pthread', '-sSHARED_MEMORY=1']

    def ice_build(self):
        self.ice_run_cmake()

    def ice_package_sources(self):
        self.ice_copy("LICENSE", src=".", dst="LICENSES/")
        self.ice_copy("*.h*", src="public/common", dst="include/common", keep_path=True)
        self.ice_copy("*.h*", src="public/client", dst="include/client", keep_path=True)
        self.ice_copy("*.h*", src="public/libbacktrace", dst="include/libbacktrace", keep_path=True)
        self.ice_copy("Tracy*.hpp", src="public/tracy", dst="include/tracy", keep_path=True)
        self.ice_copy("Tracy*.h", src="public/tracy", dst="include/tracy", keep_path=True)

    def ice_package_artifacts(self):
        # Copies done for Windows
        self.ice_copy("*.lib", src=".", dst="lib", keep_path=False)
        self.ice_copy("*.dll", src=".", dst="bin", keep_path=False)

        # Copies done for Linux and Mac
        self.ice_copy("*.dylib", src=".", dst="bin", keep_path=False)
        self.ice_copy("*.so", src=".", dst="bin", keep_path=False)
        self.ice_copy("*.a", src=".", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = ['lib']
        self.cpp_info.libs = ['TracyClient']

        if self.options.fibers:
            self.cpp_info.defines = ['TRACY_FIBERS']
        if self.options.manual_lifetime:
            self.cpp_info.defines.append('TRACY_DELAYED_INIT', 'TRACY_MANUAL_LIFETIME')
        if self.options.no_system_tracing:
            self.cpp_info.defines.append('TRACY_NO_SYSTEM_TRACING')
        if self.options.no_sampling:
            self.cpp_info.defines.append('TRACY_NO_SAMPLING')

        if self.options.shared:
            self.cpp_info.bindirs = ['bin']

            if self.settings.os == 'Linux' or self.settings.os == 'Android':
                self.cpp_info.libdirs.append('bin')
