from conans import ConanFile, tools
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
        "strip_symbols":[True, False]
    }
    default_options = {
        "shared":True,
        "double_precision": False,
        "no_export": False,
        "internal_irrxml": True,
        "fPIC": True,
        "strip_symbols":False
    }

    exports_sources = ["patches/*"]
    requires = "zlib/1.2.11@iceshard/stable"

    python_requires = "conan-iceshard-tools/0.8.2@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    def init(self):
        self.ice_init("cmake")
        self.build_requires = self._ice.build_requires

    def requirements(self):
        if not self.options.internal_irrxml:
            # Using requirement from conan-center
            self.requires.add("IrrXML/1.2@conan/stable")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    # Build both the debug and release builds
    def ice_build(self):
        self.ice_generate()
        self.ice_apply_patches()

        definitions = { }
        definitions["BUILD_SHARED_LIBS"] = self.options.shared
        definitions["ASSIMP_DOUBLE_PRECISION"] = self.options.double_precision
        definitions["ASSIMP_NO_EXPORT"] = self.options.no_export
        definitions["ASSIMP_BUILD_ASSIMP_TOOLS"] = False
        definitions["ASSIMP_BUILD_TESTS"] = False
        definitions["ASSIMP_BUILD_SAMPLES"] = False
        definitions["ASSIMP_BUILD_ZLIB"] = False
        definitions["ASSIMP_INSTALL_PDB"] = False

        # [?] There is not a single reason to have this to true in a pre-build package with explicit profiles set.
        # definitions["CONAN_DISABLE_CHECK_COMPILER"] = True

        # Disabling ASSIMP_ANDROID_JNIIOSYSTEM, failing in cmake install
        definitions["ASSIMP_ANDROID_JNIIOSYSTEM"] = False

        if self.settings.os != "Windows":
            definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC

        definitions["ASSIMP_BUILD_ALL_IMPORTERS_BY_DEFAULT"] = True
        self.ice_run_cmake(definitions=definitions)

        # Strip symbols on unix if requested
        if self.options.strip_symbols == True:
            if self.settings.build_type == "Debug":
                self.run("strip ../build/bin/libassimpd.so")
            else:
                self.run("strip ../build/bin/libassimp.so")

    def ice_package(self):
        self.copy("LICENSE.md", dst="LICENSES", keep_path=False)
        self.copy("LICENSE", dst="LICENSES", src=self._ice.source_dir, keep_path=False)

        self.copy("*.h", dst="include", src="{}/include".format(self._ice.source_dir), keep_path=True)
        self.copy("*.hpp", dst="include", src="{}/include".format(self._ice.source_dir), keep_path=True)
        self.copy("*.inl", dst="include", src="{}/include".format(self._ice.source_dir), keep_path=True)
        self.copy("*.h", dst="include_{}".format(self.settings.build_type), src="{}/include".format(self._ice.build_dir), keep_path=True)

        if self.settings.os == "Windows":
            if self.options.shared == True:
                self.copy("*.dll", dst="bin", src="{}/bin".format(self._ice.build_dir), keep_path=False)
            self.copy("*.lib", dst="lib", src="{}/lib".format(self._ice.build_dir), keep_path=False)

        if self.settings.os == "Linux":
            self.copy("*.so*", dst="bin", src="{}/bin".format(self._ice.build_dir), keep_path=False)
            self.copy("*.a", dst="lib", src="{}/lib".format(self._ice.build_dir), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = []
        self.cpp_info.libdirs = ['lib']
        self.cpp_info.bindirs = ['bin']
        self.cpp_info.includedirs.append("include_{}".format(self.settings.build_type))

        if self.settings.os == "Windows":
            compiler_ver = "vcUnknown"
            if self.settings.compiler.version == "16":
                compiler_ver = "vc142"
            if self.settings.compiler.version == "17":
                compiler_ver = "vc143"

            if self.settings.build_type == "Debug":
                self.cpp_info.libs = ["assimp-{}-mtd".format(compiler_ver)]
            else:
                self.cpp_info.libs = ["assimp-{}-mt".format(compiler_ver)]
        if self.settings.os == "Linux":
            self.cpp_info.libdirs.append("bin")
            if self.settings.build_type == "Debug":
                self.cpp_info.libs = ["assimpd"]
            else:
                self.cpp_info.libs = ["assimp"]
