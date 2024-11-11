import importlib
import subprocess
import sys
from types import ModuleType


def check_and_install(package) -> ModuleType:
    """
    Check if a Python package is installed. If not, install it using pip.

    Args:
        package (str): The name of the package to check and install.

    Returns:
        ModuleType: The imported module of the installed package.

    Raises:
        subprocess.CalledProcessError: If the installation of the package fails.
    """
    try:
        # Try to import the package to check if it's installed
        module = importlib.import_module(package)
        print(f"{package} is already installed.")
        return module  # Return the module if it's successfully imported
    except ImportError:
        # If not installed, attempt to install it
        print(f"{package} is not installed. Installing...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        # Re-import the package after installation
        module = importlib.import_module(package)
        print(f"{package} has been installed successfully.")
        return module  # Return the module after installation

if __name__ == "__main__":
    """
    Script to check and install a list of required Python packages.

    The script iterates through a predefined list of packages, checks if each 
    package is installed, and installs it if necessary. After ensuring that 
    each package is installed, it prints the version of each package.
    """
    # List of packages to check and install
    packages = [
        'torch',
        'torch_geometric',
        'pandas',
        'sklearn',
        'pyecore',
        'mlflow',
        'matplotlib'
    ]

    for package in packages:
        module = check_and_install(package)  # Get the module from the function
        # Print the version of the installed package
        print(f"{package} version: {module.__version__}")
