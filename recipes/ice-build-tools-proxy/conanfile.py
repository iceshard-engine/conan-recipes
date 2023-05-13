from conan import ConanFile
from conan import tools
from conan.tools.scm import Git
from conan.tools.files import chdir
from conan.tools.layout import basic_layout

class IceBuildToolsProxyConan(ConanFile):
    name = "ice-build-tools-proxy"
    license = "MIT"
    description = "Build tools created for the IceShard project that don't come with tailored features."
    url = "https://github.com/iceshard-engine/ice-build-tools"

    def layout(self):
        basic_layout(self)

        self.folders.source = "{}-{}".format(self.name, self.version)
        self.folders.generators = self.folders.source
        self.folders.build = self.folders.source

    def source(self):
        source_info = self.conan_data["sources"][self.version]
        if "branch" in source_info:
            git = Git(self)
            git.clone(source_info["url"], target=".")
            git.checkout(source_info["branch"])
            if "commit" in source_info:
                git.checkout(source_info["commit"])
        elif "tag" in source_info:
            git = Git(self)
            git.clone(source_info["url"], target=".")
            git.checkout(source_info["tag"])

    def build(self):
        self.run("conan create . --version {} --user {} --channel {}".format(self.version, self.user, self.channel))
