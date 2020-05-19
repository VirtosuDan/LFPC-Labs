import copy
import string
INPUT = open('test.txt').read().split('\n')
eps = 'epsilon'
def readProdutions(inputArr, arrow='---->'): #function that reads the productions from the file
    input = {}
    for el in inputArr:
        x = el.split(arrow)
        if not x[0] in input:
            input[x[0]] = []
        input[x[0]].append(x[1])
    return input

def eliminateEpsilonProductions(productions): #a function that removes Epsilon productions if they exist
    def _haveEpsilon(productions):
        for key in productions:
            for el in productions[key]:
                if el == eps:
                    return True, key
        return False, None
    locProductions = copy.deepcopy(productions)
    haveEpsilon, epsKey = _haveEpsilon(locProductions)
    while haveEpsilon:
        locProductions[epsKey].remove(eps)
        if len(locProductions[epsKey]) == 0:
            del locProductions[epsKey]

        for key in locProductions:
            for i, el in enumerate(locProductions[key]):
                if epsKey in el:
                    if epsKey in locProductions:
                        count = el.count(epsKey)
                        arr = [i for i in range(1, count + 1)]
                        subSets = [x for x in getAbsencePowerSet(arr)]
                        toAdd = change(el, epsKey, subSets)[:-1]
                        toAdd.reverse()
                        locProductions[key] = locProductions[key] + toAdd
                    else:
                        if len(locProductions[key][i]) == 1:
                            locProductions[key].remove(epsKey)
                        else:
                            locProductions[key][i] = el.replace(epsKey, '')
        haveEpsilon, epsKey = _haveEpsilon(locProductions)
    return locProductions

def eliminateRenamings(productions): #function that eliminates the Renamings if they exist.
    def isRenaming(key, productions):
        for el in productions[key]:
            if (len(el) == 1) and (el in productions):
                return True, el
        return False, None
    def remove(key, initialValue, productions):
        haveRenaming, value = isRenaming(initialValue, productions)

        if haveRenaming:
            productions = remove(initialValue, value, productions)

        productions[key].remove(initialValue)
        productions[key] = productions[key] + productions[initialValue]
        return productions
    locProductions = copy.deepcopy(productions)
    for key in locProductions:
        haveRenaming, val = isRenaming(key, locProductions)
        if haveRenaming:
            locProductions = remove(key, val, locProductions)
    return locProductions

def eliminateInaccesibleSymbols(productions): #function that removes the Non-Accessible symbols
    locProductions = copy.deepcopy(productions)
    accessedKeys = set()

    for key in locProductions:
        for el in locProductions[key]:
            for letter in el:
                if (letter in locProductions):
                    accessedKeys.add(letter)

    for key in list(locProductions):
        if key not in accessedKeys:
            del locProductions[key]
    return locProductions


def eliminateNonProductiveSymbols(productions): #function that eliminates the non productive symbols
    locProductions = copy.deepcopy(productions)
    productives = set()

    for key in locProductions:
        for el in locProductions[key]:
            if (len(el) == 1) and (el not in locProductions):
                productives.add(key)

    callStack = 1
    while callStack:
        for key in locProductions:
            if key in productives:
                continue

            for el in locProductions[key]:
                for letter in el:
                    if (letter in productives):
                        productives.add(key)
                        callStack += 1
        callStack -= 1

    for key in list(locProductions):
        if key not in productives:
            del locProductions[key]

            for innerKey in list(locProductions):
                for el in locProductions[innerKey]:
                    if key in el:
                        locProductions[innerKey].remove(el)
    return locProductions

def newSymbol(position, productions): #Add new NonTerminal Symbol for CNF
    letters = string.ascii_uppercase
    while letters[position] in productions:
        position -= 1
    return letters[position], position

def normalizationToCNF(productions): #function that produces the Normalization According to the Chomsky rules.ss
    locProductions = copy.deepcopy(productions)
    temp = {}
    terminals = string.ascii_lowercase
    lettersCounter = len(string.ascii_uppercase) - 1


    callStack = 1
    while callStack:
        for key in list(locProductions):
            for i, el in enumerate(locProductions[key]):
                if len(el) > 2:
                    if el in temp:
                        locProductions[key][i] = temp[el]
                    else:
                        symbol, lettersCounter = newSymbol(lettersCounter, locProductions)
                        temp[el] = symbol + el[len(el) - 1]
                        locProductions[symbol] = [el[:len(el) - 1]]
                        locProductions[key][i] = temp[el]
                        callStack += 1
        callStack -= 1
        def _containsTerminal(str):
            for letter in str:
                if letter in string.ascii_lowercase:
                    return True
            return False

    for key in list(locProductions):
        for i, el in enumerate(locProductions[key]):
            if len(el) == 2 and _containsTerminal(el):
                if el in temp:
                    locProductions[key][i] = temp[el]
                else:
                    for letter in el:
                        if letter in terminals:
                            if letter in temp:
                                locProductions[key][i] = locProductions[key][i].replace(letter, temp[letter])
                            else:
                                symbol, lettersCounter = newSymbol(lettersCounter, locProductions)
                                temp[letter] = symbol
                                locProductions[temp[letter]] = [letter]
                                locProductions[key][i] = locProductions[key][i].replace(letter, temp[letter])
                    temp[el] = locProductions[key][i]
    return locProductions

def getAbsencePowerSet(seq):
    if len(seq) <= 1:
        yield seq
        yield []
    else:
        for item in getAbsencePowerSet(seq[1:]):
            yield [seq[0]] + item
            yield item

def change(str, subStr, mask):
    result = []
    for m in mask:
        modified = str
        pos = 1
        for i in m:
            for _ in range(i):
                pos = modified.find(subStr, pos - i)
            modified = modified[:pos] + modified[pos + 1:]
        result.append(modified)
    return result

def showGrammar(productions):
    print("The Grammar in Chomsky Normal Form is:")
    for key in productions:
        print(key, '---->', productions[key],';')

productions = readProdutions(INPUT)
productions = eliminateEpsilonProductions(productions)
productions = eliminateRenamings(productions)
productions = eliminateInaccesibleSymbols(productions)
productions = eliminateNonProductiveSymbols(productions)
productions = normalizationToCNF(productions)
showGrammar(productions)