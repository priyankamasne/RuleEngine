# RuleEngine

This a customised Rule Engine implemented in python.

Provides 3 features ->
  1) Create a new rule
  2) Edit an existing rule
  3) Validate a data unit

This engine has Command line interface.
To see the different options that are supported by this script, run the below command
>>> python src/rule.py --help

Create a new Rule 
-----------------------------------
>>> python src/rule.py --create_rule --signal ALT65 --rule '[(>,2017-01-01 22:12:30)]' --value_type datetime
>>> python src/rule.py --create_rule --signal ALT1 --rule '[(>=, 5), (<, 20)][(>, 22), (<, 30)]' --value_type integer
>>> python src/rule.py --create_rule --signal ALT2 --rule '[( != , LOW)]' --value_type string

For creating a new rule from cmdline, pass flag --create_rule along with -
1) --signal : This option specifies the key for the rule. 
              Any new dataunit checks for this key to get the corresponding rule.
              It can be any valid alphanumeric combo. ex: ALT1, ALT2 
2) --rule : This specifies the rule that any dataunit with a particular signal needs to follow.
            This has to be a list of tuples or multiple lists of tuples. ex : [(), ()][(), ()]
            Any two tuple in a list ([(), ()]) would create a condition using 'AND' condition.
            Any two lists ([ ][ ]) would create a condition using 'OR' condition
            Every tuple consist of a comparison operator and a fact to be compared against.
                  ex : (<, 10) --> '<' is the operator and '10' is a fact
                  
            Ex - 
            1) a value has to greater than equals to 5 (>=, 5) 
               and the value has to be less than 20 (<, 20)     -> '[(>=, 5), (<, 20)]'
               
            2) a value has to be greater than 20 (>, 20)
               or it has to be smaller than 5 (<, 5)            -> '[(>, 20)][(<, 5)]'
               
            Note: datetime strings have to passed in 'YYYY-mm-dd HH:mm:SS' format only
3) --value_type : This specifies the data type on which this rule has to be applied
                  Note that currently we only support 3 datatypes - string, integer, datetime
            
If a rule (signal) already exists in the rulebook, this would raise a RuleExistsError

Edit an existing rule
---------------------------------------------
>>> python src/Rule.py --edit_rule --signal ALT1 --rule '[(!=, LOW)]' --value_type String

For editing a new rule from cmdline, pass flag --edit_rule along with -
1) --signal : This should be one of the existing signals in the rulebook
2) --rule : New rule that you wish to set
3) --value_type : New value_type if you wish to set

If the rule (signal) does not exist in the rulebook, this would raise a RuleMissingError

Validate a data unit
------------------------------------------------
There are 2 ways, you can pass a dataunit
1) cmdline
    >>> python src/rule.py --data_unit --signal ALT5 --value 5 --value_type integer
    To pass a single dataunit, pass flag --data_unit along with
    a) --signal
    b) --value
    c) --value_type
2) json file input
    >>> python src/rule.py --input_file 'etc/raw_data.json'
    This file may contain multiple dataunits in json format.
    


    
