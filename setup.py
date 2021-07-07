import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name='playwright-remote',
    version='0.1.0',
    description="Enables us to execute playwright-python scripts on Pure-Python environment.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YusukeIwaki/playwright-python-remote",
    install_requires=["playwright>=1.11.0"],
    packages=setuptools.find_packages(),
)
