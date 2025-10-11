from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import copy

class RuntimeCompiledCPPRecipe(ConanFile):
    name = "rccpp"
    version = "0.1.0"
    package_type = "static-library"
    user = "iceshard"
    channel = "stable"

    # Optional metadata
    license = "zlib"
    author = "doug@enkisoftware.com"
    url = "https://github.com/RuntimeCompiledCPlusPlus/RuntimeCompiledCPlusPlus"
    description = "Runtime-Compiled C++ (RCC++) is a way to reliably make major changes to your C++ code at runtime and see the results immediately."
    topics = ("c++", "runtime-compiltaion", "hot-realod", "rccpp", "rcc++")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "LICENSE", "patches/*"

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/1.0.1@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    ice_generator = "cmake"
    ice_toolchain = "ninja"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        self.settings.compiler.cppstd = 20

    def ice_generate_cmake(self, toolchain, deps):
        super().ice_generate_cmake(toolchain, deps)
        toolchain.variables["BUILD_EXAMPLES"] = "Off"
        # This package will always enable rccpp allocator interface feature.
        toolchain.variables["RCCPP_ALLOCATOR_INTERFACE"] = "On"

    def ice_build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="Aurora")
        cmake.build()

    def ice_package_sources(self):
        self.ice_copy("LICENSE.txt", src=".", dst="LICENSES")
        self.ice_copy("*.h", src="Aurora/RuntimeCompiler", dst="include/Aurora/RuntimeCompiler", keep_path=True)
        self.ice_copy("*.h", src="Aurora/RuntimeObjectSystem", dst="include/Aurora/RuntimeObjectSystem", keep_path=True)

    def ice_package_artifacts(self):
        self.ice_copy("*.lib", src=".", dst="lib", keep_path=False)
        self.ice_copy("*.a", src=".", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.libs = ["RuntimeCompiler", "RuntimeObjectSystem"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.defines = ["RCCPP_ALLOCATOR_INTERFACE=1"]
