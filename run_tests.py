import pytest
import os

if __name__ == "__main__":
    # Указываем явный путь к тестам
    test_path = os.path.join("tests", "unit", "utils", "test_logger.py")
    pytest.main(["-v", test_path])