# Conan Recipes

This repository holds all current and past conan recipes used by IceShard projects.
Some recipes might be not be up-to-date but will be kept in the repository.

_**Note:** Currently no pull requests are accepted as the workflows only upload packages to the internal conan repository. This might change in the future._

## Accessing the packages

If you fancy to access our recipes and/or packages please see [iceshard-engine/conan-config](https://github.com/iceshard-engine/conan-config) for more details.

## The '.gitattributes'

Required to ensure that both on Windows and Linux files used in calculating the Recipe Revision Hash are exactly the same.
The problem here is, that different line endings will produce a different recipe hash, which in turn will make packages incompatible depending on which system was uploading it's recipe first.

