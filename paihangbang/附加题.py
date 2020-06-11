def Versions(version1,version2):
    if int(version1[0])>int(version2[0]):
        return 1
    elif int(version1[0])<int(version2[0]):
        return -1
    else:
        version1 = version1[1:].replace('.','').replace('0','')
        version2 = version2[1:].replace('.','').replace('0','')
        if len(version1)>len(version2):
            count = len(version1) - len(version2)
            version2 += '0' * count
        else:
            count = len(version2) - len(version1)
            version1 += '0' * count
        if version1 is '':
            version1 = 0
        if version2 is '':
            version2 = 0
        if int(version1) > int(version2):
            return 1
        elif int(version1) < int(version2):
            return -1
        else:
            return 0
