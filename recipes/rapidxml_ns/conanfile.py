from conans import ConanFile
import os

class RapidXMLNSConanRecipe(ConanFile):
    name = "rapidxml_ns"
    description = "RapidXML NS library - RapidXML with added XML namespaces support."
    url = "https://github.com/svgpp/rapidxml_ns"

    # Settings and options
    settings = "os", "compiler", "arch", "build_type"

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/0.8.2@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    def package_id(self):
        self.info.header_only()

    def init(self):
        self.ice_init("none")

    def package(self):
        self.copy("LICENSE.txt", src=self._ice.source_dir, dst="LICENSES")
        self.copy("*.hpp", src=self._ice.source_dir, dst=os.path.join("include", "rapidxml_ns"),excludes=("tests/*", "doc/*"))

    def package_info(self):
        self.cpp_info.includedirs = [ "include" ]
