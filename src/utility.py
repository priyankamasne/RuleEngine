import json


def read_json(input_file):
    """
    Method to read json

    :param input_file: path to the input json file
    :return: data read from the file
    """
    with open(input_file) as f:
        data = json.load(f)
        return data


def _convert_value_to_value_type(value, value_type):
    """
    Converts a string value_type value to 'value'
    Converts a datetime value_type value to datetime.strptime(value, '%Y-%m-%d %H:%M:%S')

    """
    if value_type == 'string':
        value = "'" + value + "'"
    elif value_type == 'datetime':
        value = "datetime.strptime('" + value + "', '%Y-%m-%d %H:%M:%S')"
    return value


def parse_rule(rule, value, value_type):
    """
    Method to parse a rule and create a final condition to evalute the rule for a given value and value_type

    :param rule: rule as read from the rule book
    :param value: value passed for a dataunit
    :param value_type: value_type of the value
    :return: return a final condition to evaluate
    """
    n = len(rule)
    idx = 0
    gbl_rule = '(1==1 '
    stack = []

    value = _convert_value_to_value_type(value, value_type)

    # import ipdb;ipdb.set_trace()
    while idx < n:
        if rule[idx] == ')':
            top = stack.pop()
            lcl_rule = ''
            while top != '(':
                lcl_rule = top + lcl_rule
                top = stack.pop()
            gbl_rule += " and " + value + lcl_rule
            idx = idx+1
        elif rule[idx] == ']':
            gbl_rule = gbl_rule + ')'
            if idx != n - 1:
                gbl_rule += ' or (1==1'
            idx = idx+1
        else:
            if rule[idx] == '(':
                stack.append(rule[idx])
                comma_idx = rule.index(',', idx)
                rule_str = rule[idx+1: comma_idx].lstrip().rstrip()
                stack.append(rule_str)

                close_brk_idx = rule.index(')', idx)
                rule_str = rule[comma_idx+1: close_brk_idx].lstrip().rstrip()
                rule_str = _convert_value_to_value_type(rule_str, value_type)
                stack.append(rule_str)
                idx = close_brk_idx
            else:
                stack.append(rule[idx])
                idx = idx+1

    return gbl_rule


class IncompleteOptionsError(Exception):
    pass


class DatatypeMismatchError(Exception):
    pass


class InvalidDatatypeError(Exception):
    pass


class RuleViolationError(Exception):
    pass


class RuleExistsError(Exception):
    pass


class RuleMissingError(Exception):
    pass