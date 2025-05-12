import logctx

#
#  Logging Arguments Example
#
print('\n\nLogging Arguments Example')
print('----------------------')


@logctx.decorators.log_arguments(['a', 'b'])
def add_numbers(a, b, c):
    print('Context inside function:', logctx.get_current().to_dict())
    # > {'a': 1, 'b': 2}
    return a + b + c


result = add_numbers(1, 2, 3)
print('Result:', result)


#
#  Logging Arguments Example with Renamed Argument
#
print('\n\nLogging Arguments Example with Renamed Argument')
print('----------------------')


@logctx.decorators.log_arguments(c='renamed_c')
def multiply_numbers(a, b, c):
    print('Context inside function:', logctx.get_current().to_dict())
    return a * b * c


result = multiply_numbers(2, 3, 4)
print('Result:', result)
