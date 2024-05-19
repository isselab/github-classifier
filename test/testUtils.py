#recursively count number of packages
def count_packages(package, count):
    for subpackage in package.subpackages:
        count += 1
        if hasattr(subpackage, 'subpackages'):
              count = count_packages(subpackage, count)
    return count

    