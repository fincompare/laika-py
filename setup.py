import setuptools


with open("README.md", "r") as fh:
	long_description = fh.read()

with open('requirements.txt') as f:
	required_packages = f.read().splitlines()


setuptools.setup(
	name="laika",
	version="0.0.3",
	author="FinCompare GmbH",
	author_email="info@fincompare.com",
	description="Python client for laika feature-flagging",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/fincompare/laika-py",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3',
	install_requires=required_packages
)
