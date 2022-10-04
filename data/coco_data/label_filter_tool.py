import os

"""
python label_filter_tool.py 

"""
current_path = os.getcwd()

data_path = current_path + "/train/"
# data_path = current_path + "/data/fall_dataset/labels/val"

file_list = os.listdir(data_path + "labels")
os.makedirs("new_labels", exist_ok=True)


for i in range(len(file_list)):

    print(file_list[i])
  
    new_text = ''

    data_check = 0

    with open(data_path + "labels/" + file_list[i], 'r') as file:
        data_list = file.readlines()

        for data in data_list:

            if data[0] == '0':
                new_text += data
                
                data_check = 1

    if data_check:

        with open('new_labels/' + file_list[i], 'w') as newfile:
            newfile.write(new_text)

    else:
        image_file_name = file_list[i][:-3] + "jpg"
        os.system("rm train/images/" + image_file_name)
        os.system("rm train/labels/" + file_list[i])
        print("delete ", file_list[i])



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