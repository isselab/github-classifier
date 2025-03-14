import autopep8


def format_python_file(path_to_file):
    try:
        # Read the current content of the file
        with open(path_to_file, 'r') as file:
            code = file.read()

        # Format the code using autopep8
        formatted_code = autopep8.fix_code(code)

        # Write the formatted code back to the file
        with open(path_to_file, 'w') as file:
            file.write(formatted_code)

        print(f"Formatted '{path_to_file}' successfully.")
    except Exception as e:
        print(f"Error formatting '{path_to_file}': {e}")


if __name__ == "__main__":
    # Specify the file path you want to format
    file_path = 'AstToEcoreConverter.py'
    format_python_file(file_path)
