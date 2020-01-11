import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="miv2datex2",
    version="0.0.1",
    author="Michaël Dierick",
    author_email="michael@dierick.io",
    description="Convert Flanders MIV traffic flow data to DATEXII",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    scripts=['miv2datex2/miv2datex2'],
    url="https://github.com/MikiDi/MIV2DATEXII",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
