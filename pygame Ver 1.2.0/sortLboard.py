def get_largest(list, start):
    '''helper method to find the largest 
    number in list starting from 
    a specific index'''

    #say the number of the index is the largest
    small = start
    for i in range(start +1, len(list)):
        if list[i]>list[small]:
            #smaller num found, update index
            small = i
    return small 

def selection_sort(list,list2):
    '''
    sorts using the selection sort algorhithm
    '''
    #iterate for num items in list
    for item in range(len(list)):
    #call get largest function which 
    #finds the largest value in the list 
        largest = get_largest(list,item)
            
        if largest != item:
        #swap current element with 
        #largest if any
            list[largest],list[item]=list[item],list[largest]
            list2[largest],list2[item] = list2[item],list2[largest]
    return list,list2



def save_highscore(name,score):
    string_devider = ":"
    with open('username.txt','r+') as file:

        data = file.readlines()
        list = data
        #print(data)

        for row in range(len(data)):

          details = data[row]

          for i in range(len(details)):
            if details[i] == string_devider and details[i]:

              string_dev_pos = i
              
              db_name = details[:string_dev_pos]          

              if db_name == name:

                data[row] = db_name+string_devider+str(score)+"\n"

            #now sort the list of names
        score_list = []
        name_list = []
        for i in list:
             d = i.strip('\n').split(':')
             name_list.append(d[0])
             score_list.append(d[1])
        print(name_list,score_list)
        
        score_list,name_list = selection_sort(score_list,name_list)
        print(name_list,score_list)
        
        for i in range(len(score_list)):
            data[i] = [str(name_list[i])+':'+str(score_list[i])]
        print(data)
    with open('username.txt','w') as file:

      for line in range(len(data)):
        file.write(data[line][0]+"\n")
        
save_highscore('Nathan',220)
