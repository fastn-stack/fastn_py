import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fastn", # Replace with your own username
    version="0.0.1",
    author="Siddhant Kumar",
    author_email="siddhantk232@gmail.com",
    description="Python package to facilitate working with fastn",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fastn-stack/fastn_py",
    packages=setuptools.find_packages(exclude=['tests*']),
    install_requires=["django>=4.0", "pycryptodome"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: BSD 3-Clause",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django :: 4.0",
    ],
    python_requires='>=3.6',
)
