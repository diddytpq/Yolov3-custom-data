import os



current_path = os.getcwd()

data_path = current_path + "/fire/train_plus/"
# data_path = current_path + "/data/fall_dataset/labels/val"

file_list_1 = os.listdir(data_path + "person_labels")
file_list_2 = os.listdir(data_path + "labels")
for i in range(len(file_list_1)):

    print(file_list_1[i])

    if file_list_1[i] != file_list_2[i]:
        print("error : ", file_list_1[i], file_list_2[i])
        break

    
    new_text = ''

    with open(data_path + "person_labels/" + file_list_1[i], 'r') as file:
        data_list = file.readlines()
        
        for data in data_list:
            new_text += data

    with open(data_path + "labels/" + file_list_2[i], 'r') as file:
        data_list = file.readlines()
        
        for data in data_list:
            new_text += data


    with open('new_data/' + file_list_1[i], 'w') as newfile:
        newfile.write(new_text)

    # print(i)
    # with open(data_path + "/" + i, 'r') as file:

    #     edit_text = ''

    #     data_list = file.readlines()
        
    #     # print(data)

    #     for data in data_list:

    #         if data[0] == '0':
    #             # print(data)
    #             edit_text += '80' + data[1:]

    #         else:
    #             edit_text += '0' + data[1:]

    # with open('new_data/' + i, 'w') as newfile:
    #     newfile.write(edit_text)

# # creating a variable and storing the text
# # that we want to search
# 
  
# # creating a variable and storing the text
# # that we want to add
# 
  
# # Opening our text file in read only
# # mode using the open() function
# 
  
#     # Reading the content of the file
#     # using the read() function and storing
#     # them in a new variable
#     data = file.read()
  
#     # Searching and replacing the text
#     # using the replace() function
#     data = data.replace(search_text, replace_text)
  
# # Opening our text file in write only
# # mode to write the replaced content
# with open(r'SampleFile.txt', 'w') as file:
  
#     # Writing the replaced data in our
#     # text file
#     file.write(data)
  
# # Printing Text replaced
# print("Text replaced")