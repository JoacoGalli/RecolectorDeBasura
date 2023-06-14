from setuptools import setup, find_packages

setup(
    name="ImgProcess",
    version="1.0",
    description="Funciones para procesar los buffers",
    author="nacho",
    packages= find_packages(),
    requires=['numpy','scipy.ndimage']
)