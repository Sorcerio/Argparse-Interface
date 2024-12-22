from setuptools import setup, find_packages

setup(
    name="argui",
    version="0.1.0",
    packages=find_packages(),
    install_requires=open("requirements.txt").read().splitlines(),
    entry_points={
        "console_scripts": [
            "arguidemo=argui.Demo:runDemo"
        ]
    },
    include_package_data=True,
    package_data={
        "": ["style/*.tcss"]
    },
    author="Sorcerio",
    author_email="your.email@example.com",
    description="An automatic, terminal based interactive interface for any Python 3 `argparse` command line with keyboard and mouse support.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Sorcerio/Argparse-Interface",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
