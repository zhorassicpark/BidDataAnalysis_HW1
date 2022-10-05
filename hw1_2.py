from curses.ascii import isalpha
import re
import sys
# import time
# start_time = time.time()
#time library was used to measure the ellapsed time


basketList = [] # the list that contains baskets
itemCounts = {} # the dictionary that saves the counts of each item
freqItems = []  # the list that contains only frequent items

content = sys.argv[1]
f = open(content, 'r')


while True:
    line = f.readline()
    if not line: break
    tempBasket = (lambda l: re.split(r'[^\w]+', l))(line)
    if '' in tempBasket:
        tempBasket.remove('')   # remove unnecessary blank element
    
    #remove duplicate items in one bakset and add the basket to basketlist
    tempBasket = set(tempBasket)
    tempBasket = list(tempBasket)
    basketList.append(tempBasket)

    # store the counts of each item in a basket
    for item in tempBasket:
        if item in itemCounts.keys():
            itemCounts[item] += 1
        else:
            itemCounts[item] = 1

f.close()


#filter only the items that occur more than support threshold
for key, value in itemCounts.items():
    if value >= 200:
        freqItems.append(key)

# n is the number of frequent items
n = len(freqItems)
print(n)


pairTriangleList = []       # the list that works as a data structure for triangular method
freqPairs = []              # the list that saves frequent pairs


pairTriangleList = [0 for i in range(int((n*(n-1))/2))]

#iterating all the baskets, count the support for all frequent pair candidates
for basket in basketList:
    #filter only the items that are frequent
    freqItemInBasket = []
    for item in basket:
        if item in freqItems:
            freqItemInBasket.append(item)

    #iterating for frequent items in basket, generate every pair combination
    #and add its count in triangleList
    for m in range(len(freqItemInBasket)):
        itemM = freqItemInBasket[m]
        #find the index of the item in freqItems list
        i = freqItems.index(itemM)

        for l in range(m+1, len(freqItemInBasket)):
            itemL = freqItemInBasket[l]
            j = freqItems.index(itemL)

            #add 1 to the count of the pair
            x = min(i,j)
            y = max(i,j)
            index = int(((x)*(2*n-x-1)/2) + y - x - 1)
            pairTriangleList[index] += 1
            
#iterate over the frequentPair list, and filter the pairs with counts bigger than threshold
for i in range(len(freqItems)):
    for j in range(i+1, len(freqItems)):
        index = int(((i)*(2*n-i-1)/2) + j - i - 1)
        value = pairTriangleList[index]
        if value >= 200:
            freqPairs.append(((i,j), value))

#sort the frequent Pairs with descending order of counts
freqPairs = sorted(freqPairs, key=lambda pair: pair[1], reverse=True)

print(len(freqPairs))
for i in range(min(10, len(freqPairs))):
    print(f"{freqItems[freqPairs[i][0][0]]}\t{freqItems[freqPairs[i][0][1]]}\t{freqPairs[i][1]}")


# print(f'\033[94m total ellapsed time : {time.time() - start_time} seconds \033[0m')
#time library was used to measure the ellapsed time
