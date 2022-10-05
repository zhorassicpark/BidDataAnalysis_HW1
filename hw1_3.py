from curses.ascii import isalpha
import re
import sys
import numpy as np
# import time
# start_time = time.time()
# time library was used to measure the ellapsed time

articleList = []    # a list that contains every articles
rows = []   #a list that contains every shingle that occur in articles

constB = 6  # denotes b in our homework guideline
constR = 20 # denotes r in our homework guideline
hashNum = constB*constR #length of a signature = total number of minhashing


content = sys.argv[1]
f = open(content, 'r')
while True:
    line = f.readline()
    if not line: break
    temp = line.split(' ', 1)

    #now, temp looks like [articleID, content of article]

    temp[1] = re.sub(r"[^a-zA-Z\s]", "", temp[1])
    temp[1] = ' '.join(temp[1].split())
    temp[1] = temp[1].lower()

    #now, temp looks like [articleID, cleaned content of article]

    
    shingleList = []
    for i in range(len(temp[1])-2):
        shingle = temp[1][i:i+3]
        rows.append(shingle)
        shingleList.append(shingle)
    #preventing duplicate shingle in an article
    temp[1] = list(set(shingleList))

    #now, temp looks like [articleID, [list of shingles it contains]]

    articleList.append(temp)

f.close()

#preventing duplicate shingle over all articles
rows = list(set(rows))

constN = len(rows)# denotes n in our homework guideline

# a function that determines if the input is primenumber
def isPrime(x):
    if x == 1:
        return False
    else:
        for i in range(2, int(x**0.5)+1):
            if x % i == 0:
                return False
        return True

# a function used to generate 120 sets of random a , b
def genRandMat(c): # denotes c in our homework guideline
    return np.random.randint(0,c,size=(hashNum,2))


# determine C which is the minimum primer number bigger or equal to N
constC = constN
while(True):
    if isPrime(constC):
        break
    constC += 1


#generate a 120 * 2 matrix that contains random 120 pairs of a, b for minhashing
randMat = genRandMat(constC)

#subMat is a n * 120 matrix used to store the hashed order of each rows(shingles)
subMat = np.ones((constN, hashNum))
for i in range(constN):
    for j in range(hashNum):
        subMat[i][j] = (i*randMat[j][0]+randMat[j][1])%constC



# a 120 * (num of articles) matrix to save the signatures of each articles
signatures = np.ones((hashNum, len(articleList))) * (constN + 1)


#mainMat is a (num of shingles) * (num of articles) matrix
#that contains information about whether an article contains a shingle or not
#before checking this, the matrix is initialized as zero matrix
mainMat = np.zeros((constN, len(articleList)))
for i in range(len(articleList)):
    shingles = articleList[i][1]
    for j in range(constN):
        if rows[j] in shingles:
            mainMat[j][i] = 1
            #update the signature for each hash functions when the shingle is in the article
            for k in range(hashNum):
                #compare the pre-existing value in the signature and the the value and leave the min value
                signatures[k][i] = min(signatures[k][i], subMat[j][k])





#a list that stores the candidate pairs filtered by LSH
simPairCands = []

#dicList is a list of dictionaries. each dictionary are hashtables for each bands.
#each dictionary store buckets
#each bucket is a list that can contains multiple article indices with same "signature segment(signature cut into pieces)"
dicList = [
    {},
    {},
    {},
    {},
    {},
    {}
]

#iterating over bands
for i in range(constB):
    band = signatures[constR*i:constR*(i+1), :]
    for j in range(len(articleList)):
        #signSeg stands for "signature segment", because signatures is cut into pieces by band
        signSeg = tuple(band[:, j])
        if signSeg in dicList[i].keys():#the case when other article has exactly same signSeg and has been hashed into this bucket already
            dicList[i][signSeg].append(j)
        else:#the case when this article is the first one to have this signSeg
            dicList[i][signSeg] = []
            dicList[i][signSeg].append(j)
    #iterating over hashtable, if some articles' signSegs hashed into a same bucket,
    #then make all possible combination pair for them and add them to simPairCands list.
    for key, value in dicList[i].items():
        if len(value) >= 2:
            for l in range(len(value)):
                for m in range(l+1, len(value)):
                    pair = (value[l], value[m])
                    if pair not in simPairCands:
                        simPairCands.append(pair)




#returns the intersection between two lists
def intersection(li1, li2):
    li3 = [value for value in li1 if value in li2]
    return li3

#gets actual Jaccard Similarity between to articles
def getJC(art1, art2):
    shingle1 = art1[1]
    shingle2 = art2[1]
    leninter =  len(intersection(shingle1, shingle2))
    JC = leninter / ( len(shingle1) + len(shingle2) - leninter)
    return JC

#iterating over candidate pairs of similar articles, calculate their actual Jaccard Similarity
#and filter those who have higher Jaccard Similarity larger or equal to 0.9
for pairCand in simPairCands:
    if getJC(articleList[pairCand[0]], articleList[pairCand[1]]) >= 0.9:
        print(f"{articleList[pairCand[0]][0]}\t{articleList[pairCand[1]][0]}")

# print(f'\033[94m total ellapsed time : {time.time() - start_time} seconds \033[0m')
# time library was used to measure the ellapsed time
