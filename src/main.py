import yaml
import sys
import re

def validate_name(name):
    # Check the name matches the defined regex pattern for names
    return re.fullmatch(r'[_a-zA-Z]+', name) is not None

def parse_value(key, value):
    if isinstance(value, str):
        return f'@"{value}"'  # Convert string to format if needed
    elif isinstance(value, (int, float)):
        return str(value)  # Return number as string
    elif isinstance(value, list):
        # Process list to custom array format
        return '{ ' + ', '.join(parse_value(key, v) for v in value) + ' }'
    else:
        raise SyntaxError(f"Invalid value type: {value}")

def parse_yaml(yaml_content, parent_key=''):
    output_lines = []

    for key, value in yaml_content.items():
        full_key = f"{parent_key}_{key}" if parent_key else key
        if validate_name(full_key):
            if isinstance(value, dict):
                # If it's a dictionary, we need to recurse
                output_lines.extend(parse_yaml(value, full_key))
            else:
                output_lines.append(f"def {full_key} = {parse_value(full_key, value)};")
        else:
            raise SyntaxError(f"Invalid name: {full_key}")

    return output_lines

def main(yaml_file_path, output_file_path):
    with open(yaml_file_path, 'r') as file:
        try:
            yaml_content = yaml.safe_load(file)  # Load YAML content
        except yaml.YAMLError as e:
            print(f"YAML Error: {e}")
            sys.exit(1)

    output_lines = parse_yaml(yaml_content)

    with open(output_file_path, 'w') as output_file:
        output_file.write("\n".join(output_lines))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python tool.py <input_yaml_file> <output_file>")
        sys.exit(1)

    input_yaml_file = sys.argv[1]
    output_file = sys.argv[2]
    
    main(input_yaml_file, output_file)
