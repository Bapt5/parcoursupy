import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="parcoursupy",
    version="1.0.0",
    description="Python API wrapper pour Parcoursup",
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords = ["parcoursup", "wrapper-api", "api"],
    url="https://www.github.com/Bapt5/parcoursupy",
    download_url="https://github.com/Bapt5/parcoursupy/archive/refs/tags/v1.0.0.tar.gz",
    author="Bapt5",
    author_email='drouillet.baptiste@gmail.com',
    license="MPL2.0",
    packages=setuptools.find_packages(),
    package_data={"parcoursupy": ["py.typed"]},
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.26.0",
        "beautifulsoup4>=4.10.0",
        "python-dateutil>=2.8.2"

    ]
)
