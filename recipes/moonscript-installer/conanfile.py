from conan import ConanFile
from conan.tools.scm import Git
from conan.tools.files import get, copy, rename
from os.path import join

class MoonscriptInstallerConan(ConanFile):
    name = "moonscript-installer"
    version = "0.5.0"
    license = "MIT"
    description = "Installer for the moonscript wrapper for lua. Provides the moon and moonc commane line tools."
    url = "https://github.com/leafo/moonscript"

    settings = "os"

    requires = [
        "lua/5.1.5@iceshard/stable",
        "lua-filesystem/1.8.0@iceshard/stable",
        "lua-lpeg/0.12.0@iceshard/stable"
    ]

    # Additional exports
    exports_sources = [
        "bin/moon.bat",
        "bin/moonc.bat",
        "bin/moon.sh",
        "bin/moonc.sh",
        "bin/moon_unix",
        "bin/moonc_unix",
        "bin/moon_windows",
    ]

    folder_names = {
        "moonscript": "moonscript-source",
        "alt-getopt": "alt-getopt-source",
        "argparse": "argparse-source",
        "jsonlua": "jsonlua-source",
    }

    def package_id(self):
        del self.info.settings.os

    def layout(self):
        self.folders.source = "."
        self.folders.build = "."

    def source(self):
        # source_folder = "{}-{}".format(self.name, self.version)
        dependencies = self.conan_data["sources"][self.version]

        for dep, source_info in dependencies.items():
            if "branch" in source_info:
                git = Git(self, folder=self.folder_names[dep])
                git.clone(source_info["url"], target=".")
                git.checkout(source_info["branch"])
                if "commit" in source_info:
                    git.checkout(source_info["commit"])
            elif "tag" in source_info:
                git = Git(self, folder=self.folder_names[dep])
                git.clone(source_info["url"], target=".")
                git.checkout(source_info["tag"])

    def build(self):
        rename(self, "bin/moon_unix", "bin/moon")
        rename(self, "bin/moonc_unix", "bin/moonc")

    # Export the files available in the package
    def package(self):
        # Additonal batch files to copy
        copy(self, "*", src=join(self.build_folder, "bin"), dst=join(self.package_folder, "scripts/moonscript/bin"), keep_path=False)

        for name, folder_name in self.folder_names.items():
            src = join(self.build_folder, folder_name)
            if name == "moonscript":
                dst = join(self.package_folder, "scripts/moonscript")
                copy(self, "bin/*", src=src, dst=dst, keep_path=True)
                copy(self, "moon/*", src=src, dst=dst, keep_path=True)
                copy(self, "moonscript/*", src=src, dst=dst, keep_path=True)
            else:
                copy(self, "LICENSE", src=src, dst=join(self.package_folder, "LICENSE-{}".format(name)))
                copy(self, "*.lua", src=src, dst=join(self.package_folder, "scripts/{}".format(name)), keep_path=False, excludes=["bench*", "*_spec.lua"])

    def package_info(self):
        # Enviroment info
        self.runenv_info.append_path("PATH", join(self.package_folder, "scripts/moonscript/bin"))

        if self.settings.os == "Linux":
            self.runenv_info.define("MOON_SCRIPT", join(self.package_folder, "scripts/moonscript/bin/moon"))
            self.runenv_info.define("MOONC_SCRIPT", join(self.package_folder, "scripts/moonscript/bin/moonc"))
            self.buildenv_info.define("MOONC_SCRIPT", join(self.package_folder, "scripts/moonscript/bin/moonc"))

        elif self.settings.os == "Windows":
            self.runenv_info.define("MOON_SCRIPT", join(self.package_folder, "scripts/moonscript/bin/moon.bat"))
            self.runenv_info.define("MOONC_SCRIPT", join(self.package_folder, "scripts/moonscript/bin/moonc.bat"))
            self.buildenv_info.define("MOONC_SCRIPT", join(self.package_folder, "scripts/moonscript/bin/moonc.bat"))

        # Lua paths info
        for name in self.folder_names:
            self.runenv_info.append("LUA_PATH", join(self.package_folder, "scripts/{}/?.lua".format(name)), separator=';')

        # Extra entry
        self.runenv_info.append("LUA_PATH", join(self.package_folder, "scripts/moonscript/?/init.lua"), separator=';')
