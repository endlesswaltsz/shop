
def func1(alist):
    for i in range(len(alist)):
        for j in range(len(alist)-i-1):
            if alist[j]>alist[j+1]:
                alist[j],alist[j+1]=alist[j+1],alist[j]

li=[2,3,52,24,5]
func1(li)
print(li)