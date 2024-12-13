import unittest
from unittest.mock import patch, mock_open
import yaml
from main import validate_name, evaluate_expression, parse_value, parse_yaml

class TestYamlParser(unittest.TestCase):
    def test_validate_name(self):
        self.assertTrue(validate_name("valid_name"))
        self.assertTrue(validate_name("_underscore"))
        self.assertFalse(validate_name("123invalid"))
        self.assertFalse(validate_name("invalid-name"))

    def test_evaluate_expression(self):
        context = {"x": "10", "y": "5"}
        self.assertEqual(evaluate_expression(".[+ x y]", context), 15)
        self.assertEqual(evaluate_expression(".[pow x y]", context), 10 ** 5)
        self.assertEqual(evaluate_expression(".[chr x]", context), chr(10))
        
        with self.assertRaises(SyntaxError):
            evaluate_expression(".[unsupported x y]", context)

    def test_parse_value(self):
        context = {"key": "10"}
        self.assertEqual(parse_value("key", ".[+ key 5]", context), "15")
        self.assertEqual(parse_value("key", "hello", context), "@\"hello\"")
        self.assertEqual(parse_value("key", 42, context), "42")
        self.assertEqual(parse_value("key", [1, 2, 3], context), "{ 1, 2, 3 }")

        with self.assertRaises(SyntaxError):
            parse_value("key", {"invalid": "dict"}, context)

    def test_parse_yaml(self):
        yaml_content = {
            "a": 1,
            "b": {
                "c": ".[+ 10 20]",
                "d": "text"
            }
        }
        context = {}
        expected_output = [
            "def a = 1;",
            "def b_c = 30;",
            "def b_d = @\"text\";"
        ]
        output = parse_yaml(yaml_content, context)
        self.assertEqual(output, expected_output)

    @patch("builtins.open", new_callable=mock_open, read_data="a: 1\nb: {c: .[+ 1 2], d: text}")
    def test_main_function(self, mock_file):
        with patch("main.yaml.safe_load", return_value={"a": 1, "b": {"c": ".[+ 1 2]", "d": "text"}}):
            from main import main
            main("input.yaml", "output.txt")
        mock_file.assert_any_call("output.txt", "w")
        mock_file().write.assert_called_once_with("def a = 1;\ndef b_c = 3;\ndef b_d = @\"text\";")


if __name__ == "__main__":
    unittest.main()
