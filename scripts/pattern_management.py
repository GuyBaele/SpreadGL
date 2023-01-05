import re

match_date = re.compile(r'\d+-?\d+-?\d+')
match_float = re.compile(r'(?<=\_)\d+\.?\d+')
match_coordinate = re.compile(r'-?\d+\.?\d+')
match_quoted_string = re.compile(r'\"(.*)\"')

