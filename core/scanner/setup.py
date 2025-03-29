from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

# Define the extension module
extensions = [
    Extension(
        "wifi_scanner_cy",
        ["wifi_scanner_cy.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=["-O3"],  # Optimization level
    )
]

# Setup configuration
setup(
    name="wifi_scanner_cy",
    ext_modules=cythonize(extensions, compiler_directives={
        'language_level': "3",
        'boundscheck': False,
        'wraparound': False,
        'cdivision': True,
    }),
)
