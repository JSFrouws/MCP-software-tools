from setuptools import setup, find_packages

setup(
    name="latex-compiler-mcp",
    version="0.1.0",
    description="MCP Server for LaTeX Compilation",
    author="Claude",
    author_email="example@example.com",
    packages=find_packages(),
    install_requires=[
        "mcp>=1.2.0",
        "pdf2image>=1.16.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.1.0",
            "flake8>=4.0.1",
        ],
    },
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "latex-compiler-mcp=latex_compiler.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
