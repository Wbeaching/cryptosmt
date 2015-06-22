'''
Created on Mar 28, 2014

Provides functions for constructing the input file for STP.
@author: stefan
'''


def blockCharacteristic(stpfile, characteristic, wordsize):
    """
    Excludes this characteristic from being found.
    """
    # Only add state words (x, y)
    # TODO: extend for other ciphers
    filtered_words = {var_name: var_value for var_name, var_value in
                      characteristic.characteristic_data.iteritems()
                      if var_name.startswith('x') or
                      var_name.startswith('y') or
                      var_name.startswith('v')}

    blockingStatement = "ASSERT(NOT("

    for key, value in filtered_words.iteritems():
        blockingStatement += "BVXOR({}, {}) | ".format(key, value)

    blockingStatement = blockingStatement[:-2]
    blockingStatement += ") = 0hex{});".format("0"*(wordsize / 4))
    stpfile.write(blockingStatement)
    return


def setupQuery(stpfile):
    """
    Adds the query and printing of counterexample to the stp stpfile.
    """
    stpfile.write("QUERY(FALSE);\n")
    stpfile.write("COUNTEREXAMPLE;\n")
    return


def setupVariables(stpfile, variables, wordsize):
    """
    Adds a list of variables to the stp stpfile.
    """
    stpfile.write(getStringForVariables(variables, wordsize) + '\n')
    return


def assertVariableValue(stpfile, a, b):
    """
    Adds an assert that a = b to the stp stpfile.
    """
    stpfile.write("ASSERT({} = {});\n".format(a, b))
    return


def getStringForVariables(variables, wordsize):
    """
    Takes as input the variable name, number of variables and the wordsize
    and constructs for instance a string of the form:
    x00, x01, ..., x30: BITVECTOR(wordsize);
    """
    command = ""
    for var in variables:
        command += var + ","

    command = command[:-1]
    command += ": BITVECTOR({0});".format(wordsize)
    return command


def assertNonZero(stpfile, variables, wordsize):
    stpfile.write(getStringForNonZero(variables, wordsize) + '\n')
    return


def getStringForNonZero(variables, wordsize):
    """
    Asserts that no all-zero characteristic is allowed
    """
    command = "ASSERT(NOT(("
    for var in variables:
        command += var + "|"

    command = command[:-1]
    command += ") = 0hex{}));".format("0"*(wordsize / 4))
    return command


def limitWeight(stpfile, weight, p, wordsize, ignoreMSBs=0):
    """
    Adds the weight computation and assertion to the stp stpfile.
    """
    stpfile.write("limitWeight: BITVECTOR(16);\n")
    stpfile.write(getWeightString(p, wordsize, ignoreMSBs, "limitWeight") + "\n")
    stpfile.write("ASSERT(BVLE(limitWeight, {0:#018b}));\n".format(weight))
    return


def setupWeightComputation(stpfile, weight, p, wordsize, ignoreMSBs=0):
    """
    Adds the weight computation and assertion to the stp stpfile.
    """
    stpfile.write("weight: BITVECTOR(16);\n")
    stpfile.write(getWeightString(p, wordsize, ignoreMSBs) + "\n")
    stpfile.write("ASSERT(weight = {0:#018b});\n".format(weight))
    #stpfile.write("ASSERT(BVLE(weight, {0:#018b}));\n".format(weight))
    return


def getWeightString(variables, wordsize, ignoreMSBs=0, weightVariable="weight"):
    """
    Asserts that the weight is equal to the hamming weight of the
    given variables.
    """
    if(len(variables) == 1):
        return "ASSERT({} = {});\n".format(weightVariable, variables[0])

    command = "ASSERT(({} = BVPLUS(16,".format(weightVariable)
    for var in variables:
        tmp = "0b00000000@(BVPLUS(8, "
        for bit in range(wordsize - ignoreMSBs):
            # Ignore MSBs if they do not contribute to
            # probability of the characteristic.
            tmp += "0bin0000000@({0}[{1}:{1}]),".format(var, bit)
        command += tmp[:-1] + ")),"
    command = command[:-1]
    command += ")));"

    return command


def getStringEq(a, b, c, wordsize):
    command = "(BVXOR(~{0}, {1}) & BVXOR(~{0}, {2}))".format(a, b, c)
    return command


def getStringAdd(a, b, c, wordsize):
    command = "(((BVXOR((~{0} << 1)[{3}:0], ({1} << 1)[{3}:0])".format(
        a, b, c, wordsize - 1)
    command += "& BVXOR((~{0} << 1)[{3}:0], ({2} << 1)[{3}:0]))".format(
        a, b, c, wordsize - 1)
    command += " & BVXOR({0}, BVXOR({1}, BVXOR({2}, ({1} << 1)[{3}:0]))))".format(
        a, b, c, wordsize - 1)
    command += " = 0hex{})".format("0"*(wordsize / 4))
    return command


def getStringForAndDifferential(a, b, c):
    """
    AND = valid(x,y,out) = (x and out) or (y and out) or (not out)
    """
    command = "(({0} & {2}) | ({1} & {2}) | (~{2}))".format(a, b, c)
    return command


def getStringLeftRotate(value, rotation, wordsize):
    if rotation % wordsize == 0:
        return "{0}".format(value)
    command = "((({0} << {1})[{2}:0]) | (({0} >> {3})[{2}:0]))".format(
        value, (rotation % wordsize), wordsize - 1, (wordsize - rotation) % wordsize)

    return command


def getStringRightRotate(value, rotation, wordsize):
    if rotation % wordsize == 0:
        return "{0}".format(value)
    command = "((({0} >> {1})[{2}:0]) | (({0} << {3})[{2}:0]))".format(
        value, (rotation % wordsize), wordsize - 1, (wordsize - rotation) % wordsize)
    return command