from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_des = str(f.read())

setup(
    name='flet_ivid_hks',
    version='1.4',
    author='SKbarbon, Hocassian',
    description='A package tool that provide basic video player and easy clip for flet.',
    long_description=long_des,
    long_description_content_type='text/markdown',
    url='https://github.com/Uni-Gal/fork-flet_ived',
    install_requires=["flet", "opencv-python"],
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows"
    ],
)