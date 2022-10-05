from curses.ascii import isalpha
import re
import sys
from pyspark import SparkConf, SparkContext
# import time
# start_time = time.time()
#time library was used to measure the ellapsed time


conf = SparkConf()
sc = SparkContext(conf=conf)


def pickRepresentativeAndOthers(friendsList):
    representativeFriendAndOthers = []
    for i in range(1, len(friendsList)):
        # the below means, friends[i] is friend[0]'s friend
        # and friend[0] has another friends [list of friend[0]'s friends except friend[1]]]
        representativeFriendAndOthers.append((friendsList[i], (friendsList[0], [*friendsList[1:i], *friendsList[i+1:len(friendsList)]])))
    return representativeFriendAndOthers


lines = sc.textFile(sys.argv[1])
usersFriendList = lines.map(lambda l: re.split(r'[^\w]+', l))
#usersFriendList's each element looks like (userId, [user's friends IDs])

representativeFriendAndOthers = usersFriendList.flatMap(pickRepresentativeAndOthers)
groupedByCommonFriend = representativeFriendAndOthers.groupByKey()
#now, representativeFriendAndOthers have become grouped by common friends.
#the tuples with same key are potentially to have a common friend "key"

def combinationOfNodes(nodeTuple):
    nodeList = list(nodeTuple[1])
    candidates = []

    #make a combination for the friends with same keys,
    #if they are not friends to each other, than they are candidate pair
    #these process will be repeated for a pair as number of their common friends
    for i in range(len(nodeList)):
        for j in range(i+1, len(nodeList)):
            if nodeList[j][0] not in nodeList[i][1]:
                smallFriend=  min(nodeList[i][0], nodeList[j][0])
                bigFriend=  max(nodeList[i][0], nodeList[j][0])
                candidates.append(((smallFriend, bigFriend),1))
    return candidates

candidates = groupedByCommonFriend.flatMap(combinationOfNodes)

#reduce by key again the candidates.
#then the same pairs gather together.
#summing up their values, we can get a pair's total number of common friends
recommendations = candidates.reduceByKey(lambda i,j: i+j)

#sort the potential friends pairs.
#it should be ordered descending for the 'count' so we are ordering ascending by ' - count'
sortedRecommendations = recommendations.sortBy(lambda l: (-l[1], l[0][0], l[0][1]))

result = sortedRecommendations.collect()

for i in range(min(len(result), 10)):
    print(f"{result[i][0][0]}\t{result[i][0][1]}\t{result[i][1]}")
sc.stop()


# print(f'\033[94m total ellapsed time : {time.time() - start_time} seconds \033[0m')
#time library was used to measure the ellapsed time
