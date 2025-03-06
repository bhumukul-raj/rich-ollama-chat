from setuptools import setup, find_packages

setup(
    name="rich-ollama-chat",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "rich>=13.0.0",
        "ollama>=0.1.0",
    ],
    author="Bhumukul Raj",
    author_email="bhumukulraj@gmail.com",
    description="A beautiful terminal-based chat interface for Ollama using Rich formatting",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/bhumukul-raj/rich-ollama-chat",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "rich-ollama-chat=rich_ollama_chat.cli:main",
        ],
    },
) 