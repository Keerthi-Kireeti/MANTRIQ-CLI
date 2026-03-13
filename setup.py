from setuptools import setup, find_packages

setup(
    name="mantriq",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
        "prompt-toolkit>=3.0.38",
        "langchain>=0.2.0",
        "langchain-community>=0.2.0",
        "langchain-ollama>=0.1.0",
        "langchain-core>=0.2.0",
        "ollama>=0.2.0",
        "pydantic>=2.0.0",
        "requests>=2.31.0",
        "pyfiglet>=1.0.2",
    ],
    entry_points={
        "console_scripts": [
            "mantriq=mantriq.cli:app",
        ],
    },
)
