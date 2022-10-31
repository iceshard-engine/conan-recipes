from conans import ConanFile, tools
import os

class IceBuildToolsProxyConan(ConanFile):
    name = "ice-build-tools-proxy"
    license = "MIT"
    description = "Build tools created for the IceShard project that don't come with tailored features."
    url = "https://github.com/iceshard-engine/ice-build-tools"

    def source(self):
        source_folder = "{}-{}".format(self.name, self.version)
        source_info = self.conan_data["sources"][self.version]

        if "branch" in source_info:
            git = tools.Git(folder=source_folder)
            git.clone(source_info["url"], source_info["branch"])
            if "commit" in source_info:
                git.checkout(source_info["commit"])
        elif "tag" in source_info:
            git = tools.Git(folder=source_folder)
            git.clone(source_info["url"], source_info["tag"])

    def build(self):
        with tools.chdir("{}-{}".format(self.name, self.version)):
            self.run("conan create . ice-build-tools/{}@{}/{}".format(self.version, self.user, self.channel))
