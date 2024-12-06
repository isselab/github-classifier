import os.path
import subprocess

def run_tests():
    # Set dir to test dir:
    test_directory = os.path.dirname(os.path.abspath(__file__))
    # Run tests with coverage
    subprocess.run(["coverage", "run", "-m", "unittest", "discover"],cwd = test_directory)

    # Generate coverage report
    subprocess.run(["coverage", "report"],cwd = test_directory)
    subprocess.run(["coverage", "html"],cwd = test_directory)

if __name__ == "__main__":
    run_tests()