from conan import ConanFile
from conan import tools
from conan.tools.scm import Git
from conan.tools.files import chdir

class IceBuildToolsProxyConan(ConanFile):
    name = "ice-build-tools-proxy"
    license = "MIT"
    description = "Build tools created for the IceShard project that don't come with tailored features."
    url = "https://github.com/iceshard-engine/ice-build-tools"

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
        with chdir("{}-{}".format(self.name, self.version)):
            self.run("conan create . --version {} --user {} --channel {}".format(self.version, self.user, self.channel))
