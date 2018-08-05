#!/usr/local/bin/python
"""

rule.py [<options>] [...args...]

Rule Engine

Author: Priyanka Masne, 20180805

"""
from datetime import datetime
from optparse import OptionParser
from utility import (DatatypeMismatchError,
                     IncompleteOptionsError,
                     InvalidDatatypeError,
                     parse_rule, read_json,
                     RuleExistsError,
                     RuleMissingError,
                     RuleViolationError)

import json


class DataUnit:
    """
    Class for validation of DataUnits

    """
    def __init__(self, signal, value, value_type):
        self.signal = signal
        self.value = value
        self.value_type = value_type.lower()

    @classmethod
    def from_dict(cls, data_unit):
        """
        DataUnit class excepts the user to explicitly pass signal, value, value_type for every dataunit.
        Sometime, a user may want to pass a dataunit as dictionary of the 3 parameters.
        This classmethod enables that feature in this class.

        :param data_unit: Dictionary of signal, value and value_type
        :return: DataUnit class object
        """
        return cls(data_unit['signal'], data_unit['value'], data_unit['value_type'])

    def _verify_value_type(self):
        """
        Currently our RuleEngine only supports 3 datatype - string, integer, datetime.
        If a dataunit's value_type is not one of these, this method raises InvalidDatatypeError.

        """
        if self.value_type not in ('string', 'integer', 'datetime'):
            raise InvalidDatatypeError("InvalidDatatypeError: invalid data type")

    def _verify_value_against_value_type(self):
        """
        Method to check if the value passed in the dataunit matches the value_type passed.
        Raises DatatypeMismatchError is it does not match.

        """
        try:
            if self.value_type == 'integer':
                val = int(self.value)
                if not isinstance(val, int):
                    raise DatatypeMismatchError("DatatypeMismatchError: The value passed is not an integer type but long type")
            if self.value_type == 'datetime':
                # TODO: support datetime formats other than 'YYYY-mm-dd HH:MM:ss'
                date_format = '%Y-%m-%d %H:%M:%S'
                datetime.strptime(self.value, date_format)
        except ValueError:
            raise DatatypeMismatchError("DatatypeMismatchError: value does not match with value_type")

    def _verify_value_against_rule(self):
        """
        Method to check if the dataunit agrees to the rule defined for the corresponding signal.
        If the rule for the signal does not exists, it raises RuleMissingError.
        If the value_type in dataunit does not match the value_type defined in the rule, it raises RuleViolationError
        If the value in dataunit does not satisfy the rule, it raises RuleViolationError

        """
        rules = read_json('etc/rule_book.json')
        rule = rules[0].get(self.signal, 0)
        if not rule:
            raise RuleMissingError("RuleMissingError: Rule for signal %s does not exist."
                                   "Please create the rule first. " % self.signal)
        if self.value_type != rule['value_type'].lower():
            raise RuleViolationError('RuleViolationError: value_type for the data unit does not match '
                                     'the value_type defined in the rule for signal %s' % (self.signal))
        s = parse_rule(rule['rule'], self.value, self.value_type)
        if not eval(s):
            raise RuleViolationError('RuleViolationError: value does not match the rule')

    def validate_data_unit(self):
        """
        Method to validate the dataunit and raise appropriate Exception in case of violation of the rules

        """
        try:
            # import ipdb;ipdb.set_trace()
            self._verify_value_type()
            self._verify_value_against_value_type()
            self._verify_value_against_rule()
        except (InvalidDatatypeError, DatatypeMismatchError, ValueError, RuleViolationError) as e:
            raise e


class Rule:
    """
    Rule Class
    """
    def __init__(self, signal, rule, value_type):
        self.signal = signal
        self.rule = rule
        self.value_type = value_type

    def create_rule(self):
        """
        Method to create new rules.
        If rule for a signal already exists, it raises RuleExistsError.
        Otherwise dumps the new rule into existing rule book.

        """
        rules = read_json('etc/rule_book.json')
        if self.signal in rules[0].keys():
            raise RuleExistsError("RuleExistsError: Rule for signal %s already exists."
                                  "Please edit the rule if you wish to "
                                  "make changes to the existing rule" % self.signal)
        rules[0][self.signal] = {}
        rules[0][self.signal]['rule'] = self.rule
        rules[0][self.signal]['value_type'] = self.value_type.lower()
        with open('etc/rule_book.json', 'w') as f:
            json.dump(rules, f)

    def edit_rule(self):
        """
        Method to edit an existing rule.
        If rule for the signal passed does not exist, it raises RuleMissingError.
        Otherwise, edits the rule and dumps it back into the rule book

        """
        rules = read_json('etc/rule_book.json')
        if self.signal not in rules[0].keys():
            raise RuleMissingError("RuleMissingError: Rule for signal %s does not exist."
                                   "Please create the rule first. " % self.signal)
        rules[0][self.signal]['rule'] = self.rule
        rules[0][self.signal]['value_type'] = self.value_type.lower()
        with open('etc/rule_book.json', 'w') as f:
            json.dump(rules, f)


def getopts():
    """
    Parse the command-line options

    """
    parser = OptionParser()

    parser.add_option("-d", "--data_unit", action="store_true",
                      help="This is to enter a data unit. "
                           "A data unit would have three keys - signal, value, value_type. ")
    parser.add_option("-s", "--signal",
                      help="This key specifies the source ID of the signal. "
                           "It could be any valid alphanumeric combo. "
                           "ex: ATL1, ATL2, ATL3, ATL4")
    parser.add_option("-v", "--value",
                      help="This would be the actual value of the signal. "
                           "This would always be a string. "
                           "ex: '234', 'HIGH', 'LOW', '23/07/2017'")
    parser.add_option("-t", "--value_type",
                      help="This would specify how the value is to interpreted. "
                           "It would be one of the following "
                           "Integer: In this case the value is interpreted to be an integer. "
                           "    Ex: '234' would be interpreted as 234"
                           "String: In this case the value is interpreted to be a String. "
                           "    Ex: 'HIGH' would be interpreted as 'HIGH'"
                           "Datetime: In this case the value is interpreted to be a Date Time.")
    parser.add_option("-e", "--edit_rule", action="store_true",
                      help="This is to edit an existing rule. "
                           "To edit a rule, three keys are required - signal, value_type, rule")
    parser.add_option("-c", "--create_rule", action="store_true",
                      help="This is to create a new rule"
                           "To create a rule, three keys are required - signal, value_type, rule")
    parser.add_option("-r", "--rule",
                      help="This is to define the rule")
    parser.add_option("-f", "--input_file",
                      help="This is path to the file which gives a bunch of inputs to test")

    opts, args = parser.parse_args()
    return opts, args


def main():
    opts, args = getopts()

    if opts.data_unit:
        if not opts.signal or not opts.value or not opts.value_type:
            raise IncompleteOptionsError("\nA new data unit must have a signal, a value and a value_type. \n"
                                    "One or more of these options are missing, make sure to pass all the \n"
                                    "three when passing a data_unit flag. \n"
                                    "Please refer to help section of the script to understand each of these options. \n")
        du = DataUnit(opts.signal, opts.value, opts.value_type)
        try:
            du.validate_data_unit()
            print "Valid data unit {%s, %s, %s}" % (opts.signal, opts.value, opts.value_type)
        except (InvalidDatatypeError, DatatypeMismatchError, ValueError, RuleViolationError) as e:
            raise e
    elif opts.input_file:
        datafile = read_json(opts.input_file)
        for dataunit in datafile:
            print "-------------------------------------------------------"
            print "data_unit -> ", dataunit
            try:
                du = DataUnit.from_dict(dataunit)
                du.validate_data_unit()
                print "Valid data unit"
            except (InvalidDatatypeError, DatatypeMismatchError, ValueError, RuleViolationError) as e:
                # TODO: use python logging module to log the exceptions
                print str(e)
    elif opts.create_rule:
        if not opts.signal or not opts.rule or not opts.value_type:
            raise IncompleteOptionsError("\nA new rule must have a signal, a rule and a value_type. \n"
                                    "One or more of these options are missing, make sure to pass all the \n"
                                    "options when passing a create_rule flag. \n"
                                    "Please refer to help section of the script to understand each of these options. \n")
        r = Rule(opts.signal, opts.rule, opts.value_type)
        try:
            r.create_rule()
        except RuleExistsError as e:
            raise e
    elif opts.edit_rule:
        if not opts.signal or not opts.rule or not opts.value_type:
            raise IncompleteOptionsError("\nA new rule must have a signal, a rule and a value_type. \n"
                                    "One or more of these options are missing, make sure to pass all the \n"
                                    "options when passing a create_rule flag. \n"
                                    "Please refer to help section of the script to understand each of these options. \n")
        r = Rule(opts.signal, opts.rule, opts.value_type)
        try:
            r.edit_rule()
        except RuleMissingError as e:
            raise e


if __name__ == '__main__':
    main()
