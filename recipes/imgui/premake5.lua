newoption {
    trigger = "arch",
    description = "Build for the given architecture",
    value = "ARCH"
}

newoption {
    trigger = "docking_branch",
    description = "Does nothing in the premake, is used to get proper source files from github."
}

newoption {
    trigger = "fPIC",
    description = "Enabled Position Independent Code generation on GCC and Clang"
}

workspace "imgui"
    configurations { "Debug", "Release" }

    architecture(_OPTIONS.arch)

    filter { "Debug" }
        symbols "On"

    filter { "Release" }
        optimize "On"

    project "imgui"
        kind("StaticLib")

        includedirs {
            "."
        }

        files {
            "*.h",
            "*.cpp",
        }

        pic(_OPTIONS.fPIC and "On" or "Off")

        filter "toolset:msvc"
            files { "misc/natvis/*.natvis" }
