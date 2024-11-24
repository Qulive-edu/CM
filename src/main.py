import yaml
import sys
import re

def validate_name(name):
    # Check the name matches the defined regex pattern for names
    return re.fullmatch(r'[_a-zA-Z]+', name) is not None

def evaluate_expression(expression, context):
    """Evaluate the expression using the current context."""
    # Remove the leading `.[` and trailing `]`
    expression = expression[2:-1].strip()
    
    # Split the expression into parts
    tokens = expression.split()
    operator = tokens[0]  # The first token is the operator
    operands = tokens[1:]  # The remaining are operands

    # Map the operands to their evaluated values
    evaluated_operands = []
    for operand in operands:
        if operand in context:
            evaluated_operands.append(int(context[operand]))
        else:
            evaluated_operands.append(int(operand))  # Convert directly to float if it's a number

    # Simple evaluation based on operator
    if operator == '+':
        return sum(evaluated_operands)
    elif operator == 'pow':
        return evaluated_operands[0] ** evaluated_operands[1]
    elif operator == 'chr':
        return chr(int(evaluated_operands[0]))
    else:
        raise SyntaxError(f"Unsupported operator: {operator}")

def parse_value(key, value, context):
    if isinstance(value, str):
        value = value.strip()
        if value.startswith('.[') and value.endswith(']'):
            # If value is an expression to evaluate
            evaluated = evaluate_expression(value, context)
            return str(evaluated)
        return f'@"{value}"'  # Convert string to format if needed
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, list):
        return '{ ' + ', '.join(parse_value(key, v, context) for v in value) + ' }'
    else:
        raise SyntaxError(f"Invalid value type: {value}")

def parse_yaml(yaml_content, context, parent_key=''):
    output_lines = []

    for key, value in yaml_content.items():
        full_key = f"{parent_key}_{key}" if parent_key else key
        if validate_name(full_key):
            if isinstance(value, dict):
                output_lines.extend(parse_yaml(value, context, full_key))
            else:
                # Parse the value and add to context
                context[full_key] = parse_value(full_key, value, context)
                output_lines.append(f"def {full_key} = {context[full_key]};")
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

    context = {}
    output_lines = parse_yaml(yaml_content, context)

    with open(output_file_path, 'w') as output_file:
        output_file.write("\n".join(output_lines))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python tool.py <input_yaml_file> <output_file>")
        sys.exit(1)

    input_yaml_file = sys.argv[1]
    output_file = sys.argv[2]
    
    main(input_yaml_file, output_file)
