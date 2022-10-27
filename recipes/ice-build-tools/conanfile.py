from conans import ConanFile, tools
import os

class IceBuildToolsConan(ConanFile):
    name = "ice-build-tools"
    license = "MIT"
    description = "Build tools created for the IceShard project that don't come with tailored features."
    url = "https://github.com/iceshard-engine/ice-build-tools"

    settings = "os"
    requires = "moonscript-installer/0.5.0@iceshard/stable"

    exports_sources = [ "source/*", "scripts/*", "LICENSE" ]

    def package_id(self):
        del self.info.settings.os

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
            if self.settings.os == "Windows":
                self.run("%MOONC_SCRIPT% source/ice -t build")
            if self.settings.os == "Linux":
                self.run("lua $MOONC_SCRIPT source/ice -t build")

    def package(self):
        source_folder = "{}-{}".format(self.name, self.version)
        self.copy("LICENSE", src=source_folder, dst="LICENSE", keep_path=False)
        self.copy("*.lua", src=source_folder + "/build/", dst="scripts/lua/", keep_path=True)
        self.copy("*.*", src=source_folder + "/scripts/shell/", dst="scripts/shell/", keep_path=False)
        self.copy("*.bff", src=source_folder + "/scripts/fastbuild/", dst="scripts/fastbuild/", keep_path=True)

    def package_info(self):
        self.env_info.LUA_PATH.append(os.path.join(self.package_folder, "scripts/lua/?.lua"))
        self.env_info.LUA_PATH.append(os.path.join(self.package_folder, "scripts/lua/?/init.lua"))

        self.env_info.ICE_BUILT_TOOLS_VER = self.version
        self.env_info.ICE_FBUILD_SCRIPTS = os.path.join(self.package_folder, "scripts/fastbuild")
        if self.settings.os == "Windows":
            self.env_info.ICE_SCRIPT = os.path.join(self.package_folder, "scripts/shell/build_win.bat")
        if self.settings.os == "Linux":
            self.env_info.ICE_SCRIPT = os.path.join(self.package_folder, "scripts/shell/build_linux.sh")