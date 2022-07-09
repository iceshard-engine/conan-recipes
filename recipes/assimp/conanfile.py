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
    }
    default_options = {
        "shared":True,
        "double_precision": False,
        "no_export": False,
        "internal_irrxml": True,
        "fPIC": True
    }

    # Format available options
    _format_option_map = {
        "with_3d": "ASSIMP_BUILD_3D_IMPORTER",
        "with_3ds": "ASSIMP_BUILD_3DS_IMPORTER",
        "with_3mf": "ASSIMP_BUILD_3MF_IMPORTER",
        "with_ac": "ASSIMP_BUILD_AC_IMPORTER",
        "with_amf": "ASSIMP_BUILD_AMF_IMPORTER",
        "with_ase": "ASSIMP_BUILD_ASE_IMPORTER",
        "with_assbin": "ASSIMP_BUILD_ASSBIN_IMPORTER",
        "with_assxml": "ASSIMP_BUILD_ASSXML_IMPORTER",
        "with_b3d": "ASSIMP_BUILD_B3D_IMPORTER",
        "with_blend": "ASSIMP_BUILD_BLEND_IMPORTER",
        "with_bvh": "ASSIMP_BUILD_BVH_IMPORTER",
        "with_cob": "ASSIMP_BUILD_COB_IMPORTER",
        "with_collada": "ASSIMP_BUILD_COLLADA_IMPORTER",
        "with_csm": "ASSIMP_BUILD_CSM_IMPORTER",
        "with_dxf": "ASSIMP_BUILD_DXF_IMPORTER",
        "with_fbx": "ASSIMP_BUILD_FBX_IMPORTER",
        "with_gltf": "ASSIMP_BUILD_GLTF_IMPORTER",
        "with_hmp": "ASSIMP_BUILD_HMP_IMPORTER",
        "with_ifc": "ASSIMP_BUILD_IFC_IMPORTER",
        "with_irr": "ASSIMP_BUILD_IRR_IMPORTER",
        "with_irrmesh": "ASSIMP_BUILD_IRRMESH_IMPORTER",
        "with_lwo": "ASSIMP_BUILD_LWO_IMPORTER",
        "with_lws": "ASSIMP_BUILD_LWS_IMPORTER",
        "with_md2": "ASSIMP_BUILD_MD2_IMPORTER",
        "with_md3": "ASSIMP_BUILD_MD3_IMPORTER",
        "with_md5": "ASSIMP_BUILD_MD5_IMPORTER",
        "with_mdc": "ASSIMP_BUILD_MDC_IMPORTER",
        "with_mdl": "ASSIMP_BUILD_MDL_IMPORTER",
        "with_mmd": "ASSIMP_BUILD_MMD_IMPORTER",
        "with_ms3d": "ASSIMP_BUILD_MS3D_IMPORTER",
        "with_ndo": "ASSIMP_BUILD_NDO_IMPORTER",
        "with_nff": "ASSIMP_BUILD_NFF_IMPORTER",
        "with_obj": "ASSIMP_BUILD_OBJ_IMPORTER",
        "with_off": "ASSIMP_BUILD_OFF_IMPORTER",
        "with_ogre": "ASSIMP_BUILD_OGRE_IMPORTER",
        "with_opengex": "ASSIMP_BUILD_OPENGEX_IMPORTER",
        "with_ply": "ASSIMP_BUILD_PLY_IMPORTER",
        "with_q3bsp": "ASSIMP_BUILD_Q3BSP_IMPORTER",
        "with_q3d": "ASSIMP_BUILD_Q3D_IMPORTER",
        "with_raw": "ASSIMP_BUILD_RAW_IMPORTER",
        "with_sib": "ASSIMP_BUILD_SIB_IMPORTER",
        "with_smd": "ASSIMP_BUILD_SMD_IMPORTER",
        "with_stl": "ASSIMP_BUILD_STL_IMPORTER",
        "with_terragen": "ASSIMP_BUILD_TERRAGEN_IMPORTER",
        "with_x": "ASSIMP_BUILD_X_IMPORTER",
        "with_x3d": "ASSIMP_BUILD_X3D_IMPORTER",
        "with_xgl": "ASSIMP_BUILD_XGL_IMPORTER",
    }
    options.update(dict.fromkeys(_format_option_map, [True, False]))
    default_options.update(dict.fromkeys(_format_option_map, True))

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
        definitions["SYSTEM_IRRXML"] = not self.options.internal_irrxml
        definitions["BUILD_SHARED_LIBS"] = self.options.shared
        definitions["ASSIMP_DOUBLE_PRECISION"] = self.options.double_precision
        definitions["ASSIMP_NO_EXPORT"] = self.options.no_export
        definitions["ASSIMP_BUILD_ASSIMP_TOOLS"] = False
        definitions["ASSIMP_BUILD_TESTS"] = False
        definitions["ASSIMP_BUILD_SAMPLES"] = False
        definitions["ASSIMP_BUILD_ZLIB"] = True
        definitions["ASSIMP_INSTALL_PDB"] = False

        # [?] There is not a single reason to have this to true in a pre-build package with explicit profiles set.
        # definitions["CONAN_DISABLE_CHECK_COMPILER"] = True

        # Disabling ASSIMP_ANDROID_JNIIOSYSTEM, failing in cmake install
        definitions["ASSIMP_ANDROID_JNIIOSYSTEM"] = False

        if self.settings.os != "Windows":
            definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC

        definitions["ASSIMP_BUILD_ALL_IMPORTERS_BY_DEFAULT"] = False
        for option, definition in self._format_option_map.items():
            definitions[definition] = bool(getattr(self.options, option))

        self.ice_run_cmake(definitions=definitions)

    def package(self):
        self.copy("LICENSE.md", dst="LICENSES", keep_path=False)
        self.copy("LICENSE", dst="LICENSES", src=self._ice.source_dir, keep_path=False)

        self.copy("*.h", dst="include", src="{}/include".format(self._ice.source_dir), keep_path=True)
        self.copy("*.hpp", dst="include", src="{}/include".format(self._ice.source_dir), keep_path=True)
        self.copy("*.inl", dst="include", src="{}/include".format(self._ice.source_dir), keep_path=True)
        self.copy("*.h", dst="include_{}".format(self.settings.build_type), src="{}/include".format(self._ice.build_dir), keep_path=True)

        if self.settings.os == "Windows":
            if self.options.shared == True:
                self.copy("*.dll", dst="bin", src="{}/bin".format(self._ice.build_dir), keep_path=False)
            else:
                self.copy("zlib*.dll", dst="bin", src="{}/bin".format(self._ice.build_dir), keep_path=False)
            self.copy("*.lib", dst="lib", src="{}/lib".format(self._ice.build_dir), keep_path=False)

        if self.settings.os == "Linux":
            self.copy("*.so", dst="bin", src="{}/lib".format(self._ice.build_dir), keep_path=False)
            self.copy("*.a", dst="lib", src="{}/lib".format(self._ice.build_dir), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = []
        self.cpp_info.libdirs = ['lib']
        self.cpp_info.bindirs = ['bin']
        self.cpp_info.includedirs.append("include_{}".format(self.settings.build_type))

        if self.settings.os == "Windows":
            if self.settings.build_type == "Debug":
                self.cpp_info.libs = ["assimp-vc142-mtd", "IrrXMLd", "zlibd"]
            else:
                self.cpp_info.libs = ["assimp-vc142-mt", "IrrXML", "zlib"]
        if self.settings.os == "Linux":
            self.cpp_info.libdirs.append("bin")
            if self.settings.build_type == "Debug":
                self.cpp_info.libs = ["assimpd", "IrrXMLd", "zlibd"]
            else:
                self.cpp_info.libs = ["assimp", "IrrXML", "zlib"]
