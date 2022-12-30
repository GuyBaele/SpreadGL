import re

matchDate = re.compile(r'\d+-?\d+-?\d+')
matchFloat = re.compile(r'(?<=\_)\d+\.?\d+')
matchCoordinate = re.compile(r'-?\d+\.?\d+')
matchQuotedString = re.compile(r'\"(.*)\"')

