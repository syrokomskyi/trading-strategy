from setuptools import setup, find_packages

setup(
    name="trading-strategy",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "click>=8.0.0",
        "ccxt>=4.0.0",
        "ta>=0.10.0",
    ],
    entry_points={
        "console_scripts": [
            "trading-strategy=src.cli:main",
        ],
    },
    python_requires=">=3.11",
)
