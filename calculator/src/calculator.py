from src import operations

def calculate(num1, operation, num2):
    if operation == "+":
        return operations.add(num1, num2)
    elif operation == "-":
        return operations.subtraction(num1, num2)
    elif operation == "*":
        return operations.multiply(num1, num2)
    elif operation == "/":
        return operations.division(num1, num2)
    else:
        return "Invalid operation"