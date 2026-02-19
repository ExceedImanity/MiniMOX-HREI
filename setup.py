from setuptools import setup, find_packages

setup(
    name="minimox-hrei",
    version="1.0.0",
    author="ExceedImanity",
    description="The Hybrid Resonance Engine (HREI) - A Neuro-Symbolic AI Architecture",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ExceedImanity/MiniMOX-HREI",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache 2.0 License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.9',
    install_requires=[
        "numpy>=1.20.0",
    ],
    entry_points={
        'console_scripts': [
            'minimox=main:main',
        ],
    },
)
