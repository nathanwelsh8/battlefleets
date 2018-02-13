import time

init = round(time.clock())
counter = 0
for i in range(10000000):
    counter+=1

end = round(time.clock())

print(end-init)
