def lower_case_func(func):
    def inner():
        funct = func()
        return funct.lower()
    return inner

@lower_case_func
def test():
    return "Test Case"

print(test())