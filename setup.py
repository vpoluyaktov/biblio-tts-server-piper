"""Setup script for biblio-tts-server-piper."""

from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="biblio-tts-server-piper",
    version="0.1.0",
    author="BiblioHub Team",
    description="REST API server for Piper TTS models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vpoluyaktov/biblio-tts-server-piper",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "biblio_tts_server_piper": ["static/*", "static/**/*"],
    },
    include_package_data=True,
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "scipy>=1.11.0",
        "numpy>=1.24.0",
    ],
    entry_points={
        "console_scripts": [
            "biblio-tts-server-piper=biblio_tts_server_piper.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
)
