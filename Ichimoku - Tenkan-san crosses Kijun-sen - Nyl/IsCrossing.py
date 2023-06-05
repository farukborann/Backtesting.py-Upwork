def findFirstDifferentPoint(line1, line2):
    for i in range(len(line1)-1, -1, -1):
        if(line1[i] != line2[i]):
            return i
    
    return None

def isCrossing(line1, line2):
    _line1 = line1[:len(line1)-1]
    _line2 = line2[:len(line2)-1]

    fdp = findFirstDifferentPoint(_line1, _line2)
    if(fdp == None):
        return False

    if(line1[-1] > line2[-1] and _line1[fdp] < _line2[fdp]):
        return True

    return False

# Test method
# line1 = [10, 11, 11, 12]
# line2 = [12, 11, 11, 10]

# print(isCrossing(line1, line2))