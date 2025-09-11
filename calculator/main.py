from src import calculator

if __name__ == "__main__":
    num = float(input("Enter a number: "))
    other_num = float(input("Enter another number: "))
    operation = input("Enter an operation (add, subtract, multiply, divide): ")
    result = calculator.calculate(num, operation, other_num)

    print(result)