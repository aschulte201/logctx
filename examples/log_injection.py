import logging

import logctx

#
#   Normal Injection Example
#
print('\n\nInjection Example')
print('----------------------')


root_logger = logging.getLogger()
console_handler = logging.StreamHandler()

formatter = logging.Formatter('%(message)s %(logctx)s')
context_filter = logctx.ContextInjectingLoggingFilter(output_field='logctx')
# Alternatively omit `output_field` to add all context attributes at
# root level of each log record.

console_handler.setFormatter(formatter)
console_handler.addFilter(context_filter)

root_logger.addHandler(console_handler)
root_logger.setLevel(logging.DEBUG)

# Example usage
with logctx.new_context(user='alice'):
    root_logger.info('User logged in')


#
#   JSON Injection Example
#

# print('\n\nJSON Injection Example')
# print('----------------------')

# # pip install python-json-logger
# from pythonjsonlogger import jsonlogger

# root_logger.handlers.clear()  # reset handler from above example
# root_logger = logging.getLogger()
# console_handler = logging.StreamHandler()

# formatter = jsonlogger.JsonFormatter('%(message)s %(logctx)s')
# context_filter = logctx.ContextInjectingLoggingFilter(output_field='logctx')

# console_handler.setFormatter(formatter)
# console_handler.addFilter(context_filter)

# root_logger.addHandler(console_handler)
# root_logger.setLevel(logging.DEBUG)

# # Example usage
# with logctx.new_context(user='alice'):
#     root_logger.info('User logged in')
