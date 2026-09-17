def string_with_arrows(text, pos_start, pos_end):
    result = ''

    # Calculate indices
    idx_start = max(text.rfind('\n', 0, pos_start.index), 0)
    idx_end = text.find('\n', idx_start + 1)
    if idx_end < 0: idx_end = len(text)

    # Generate each line
    line_count = pos_end.line - pos_start.line + 1
    for i in range(line_count):
        # Calculate line columns
        line = text[idx_start:idx_end]
        col_start = pos_start.col if i == 0 else 0
        col_end = pos_end.col if i == line_count - 1 else len(line) - 1

        # Append to result
        result += line + '\n'
        result += ' ' * col_start + '^' * (col_end - col_start)

        # Re-calculate indices
        idx_start = idx_end
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0: idx_end = len(text)

    return result.replace('\t', '')

###################ERRORS##################
class Error:
    def __init__(self, start, end, error_name, details):
        self.start = start
        self.end = end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}\n'
        result += f'File {self.start.file_name}, line {self.start.line + 1}'
        result += '\n\n' + string_with_arrows(self.start.file_text, self.start, self.end)
        return result


class IllegalCharError(Error):
  def __init__(self, start, end, details):
    super().__init__(start, end, 'Illegal Character', details)

class ExpectedCharError(Error):
  def __init__(self, start, end, details):
    super().__init__(start, end, 'Expected Character', details)

class InvalidSyntaxError(Error):
  def __init__(self, start, end, details=''):
    super().__init__(start, end, 'Invalid Syntax', details)


class RTError(Error):
  def __init__(self, start, end, details, context):
    super().__init__(start, end, 'Runtime Error', details)
    self.context = context

  def as_string(self):
    result  = self.error_name + "\n" + self.details
    return result