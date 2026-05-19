def solve():
    t=int(input())

    for _ in range(t):
        n=int(input())
        arr1=list(map(int, input().split()))

        arr=[True]*n
        ans=0
        for i in range(n):
            if arr[i]%3==0:
                ans+=1
                continue
            

            

            if not arr[i]:
                while :
                if 