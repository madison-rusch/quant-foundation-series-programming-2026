import math


def main() -> None:
    try:
        text = "abcde"
        a = float(text)
    except ZeroDivisionError:
        a = 1
        print("please don't divide by zero")
    except ValueError:
        a = 0
        print("Couldn't convert, defaulted to 0")
    except Exception as e:
        print(e)
        
    print(a)
    
if __name__ == "__main__":
    main()