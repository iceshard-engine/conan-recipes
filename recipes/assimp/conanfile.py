from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import replace_in_file
import os

class AssimpConan(ConanFile):
    name = "assimp"
    license = "BSD 3-Clause"
    homepage = "https://github.com/assimp/assimp"
    url = "https://github.com/jacmoe/conan-assimp"
    description = "Open-Asset-Importer-Library that loads 40+ 3D-file-formats into one unified and clean data structure."

    # Settings and options
    settings = "os", "compiler", "arch", "build_type"
    options = {
        "shared": [True, False],
        "double_precision": [True, False],
        "no_export": [True, False],
        "internal_irrxml": [True, False],
        "fPIC": [True, False],
        "strip_symbols": [True, False]
    }
    default_options = {
        "shared":True,
        "double_precision": False,
        "no_export": False,
        "internal_irrxml": True,
        "fPIC": True,
        "strip_symbols": True
    }

    exports_sources = ["patches/*"]
    requires = "zlib/1.2.13@iceshard/stable"

    python_requires = "conan-iceshard-tools/1.0.0@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    ice_generator = "cmake"
    ice_toolchain = "cmake"

    def requirements(self):
        if not self.options.internal_irrxml:
            # Using requirement from conan-center
            self.requires.add("IrrXML/1.2@conan/stable")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.strip_symbols

    def ice_generate_cmake(self, tc, deps):
        tc.variables["CMAKE_C_COMPILER"] = str(self.settings.compiler)
        tc.variables["CMAKE_CXX_COMPILER"] = str(self.settings.compiler)

        if self.settings.compiler == 'clang':
            tc.variables["CMAKE_CXX_FLAGS_INIT"] = '-Wno-nontrivial-memcall'

        if self.settings.os == "Windows":
            main_cmake = os.path.join(self.source_folder, "CMakeLists.txt")
            replace_in_file(self, main_cmake, "ZLIB_FOUND", "zlib_FOUND")
            replace_in_file(self, main_cmake, "ZLIB_INCLUDE_DIR", "zlib_INCLUDE_DIR")

            code_cmake = os.path.join(self.source_folder, "code", "CMakeLists.txt")
            replace_in_file(self, code_cmake, "ZLIB_LIBRARIES", "zlib_LIBRARIES")

    # Build both the debug and release builds
    def ice_build(self):
        variables = { }
        variables["BUILD_SHARED_LIBS"] = self.options.shared
        variables["ASSIMP_DOUBLE_PRECISION"] = self.options.double_precision
        variables["ASSIMP_NO_EXPORT"] = self.options.no_export
        variables["ASSIMP_BUILD_ASSIMP_TOOLS"] = False
        variables["ASSIMP_BUILD_TESTS"] = False
        variables["ASSIMP_BUILD_SAMPLES"] = False
        variables["ASSIMP_BUILD_ZLIB"] = False
        variables["ASSIMP_INSTALL_PDB"] = False

        # [?] There is not a single reason to have this to true in a pre-build package with explicit profiles set.
        # variables["CONAN_DISABLE_CHECK_COMPILER"] = True

        # Disabling ASSIMP_ANDROID_JNIIOSYSTEM, failing in cmake install
        variables["ASSIMP_ANDROID_JNIIOSYSTEM"] = False

        if self.settings.os != "Windows":
            variables['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC

        variables["ASSIMP_BUILD_ALL_IMPORTERS_BY_DEFAULT"] = True
        self.ice_run_cmake(variables=variables)

        # Strip symbols on unix if requested
        if self.settings.os == "Linux":
            if self.options.strip_symbols == True:
                if self.settings.build_type == "Debug":
                    self.run("strip bin/libassimpd.so")
                else:
                    self.run("strip bin/libassimp.so")

    def ice_package_sources(self):
        self.ice_copy("LICENSE.md", src=".", dst="LICENSES", keep_path=False)
        self.ice_copy("LICENSE", src=".", dst="LICENSES", keep_path=False)

        self.ice_copy("*.h", src="include", dst="include", keep_path=True)
        self.ice_copy("*.hpp", src="include", dst="include", keep_path=True)
        self.ice_copy("*.inl", src="include", dst="include", keep_path=True)
        self.ice_copy("*.h", src="include", dst="include_{}".format(self.settings.build_type), keep_path=True)

    def ice_package_artifacts(self):
        self.ice_copy("*.dll", dst="bin", src="bin", keep_path=False)
        self.ice_copy("*.lib", dst="lib", src="lib", keep_path=False)
        self.ice_copy("*.so", dst="bin", src="bin", keep_path=False)
        self.ice_copy("*.a", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        lib_suffix = "d" if self.settings.build_type == "Debug" else ""

        self.cpp_info.libs = []
        self.cpp_info.libdirs = [ 'lib' ]
        self.cpp_info.bindirs = [ 'bin' ]
        self.cpp_info.includedirs.append("include_{}".format(self.settings.build_type))

        if self.settings.os == "Windows":
            compiler_ver = "vcUnknown"
            if self.settings.compiler.version == "192":
                compiler_ver = "vc142"
            if self.settings.compiler.version == "193":
                compiler_ver = "vc143"
            self.cpp_info.libs = ["assimp-{}-mt{}".format(compiler_ver, lib_suffix)]

        if self.settings.os == "Linux":
            self.cpp_info.libdirs.append("bin")
            self.cpp_info.libs = [ "assimp" + lib_suffix ]
