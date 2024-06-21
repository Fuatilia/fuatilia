# import os
# import re
# from doctr.io import DocumentFile
# from doctr.models import ocr_predictor

# os_path = os.path.join(os.path.expanduser('~'), 'Downloads/f_bill_vote.jpeg')

# # Load an image
# image_path = os_path

# # Create an OCR predictor
# model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)
# doc = DocumentFile.from_images(image_path)

# # Perform OCR on the image
# ocr_result = model(doc)
# result = ocr_result.export()

# # Print the extracted text
# descrepancy_string = '' 
# list_of_lines = []
# for blocks in result["pages"][0]["blocks"]: 
#     for line in blocks['lines']:
#         word_list = []
#         for word_block in line['words']:
#             word_list.append(word_block['value'])
        
#         sentence = ' '.join(word_list).replace('Hon.','')

#         sentence_l = re.findall('(?<=\d.)[A-Za-z\s\-]*', sentence)
        
#         sentence_l = [x for x in sentence_l if x !='']

#         '''
#         None of the changes /alterations  for new variables were done in place since for quick build and debugging(fallbacks)
#         '''

#         new_sentence_l = []

#         if len(sentence_l)<1 :
#             print(sentence, len(sentence_l))
#             new_sentence = sentence.lstrip().rstrip().replace('.','').replace('H ', '').replace('-','')
#             refurb_sentence_l = re.findall('(?<=\d.)[A-Za-z\s\-]*', new_sentence)

#             if len(refurb_sentence_l)<1 :
#                 print(refurb_sentence_l, len(refurb_sentence_l))
#                 descrepancy_string = descrepancy_string + sentence
#             else:
#                 list_of_lines.extend(refurb_sentence_l)
#         else:
#             for sentence_ in sentence_l:
#                 sentence = sentence_.lstrip().rstrip().replace('.','').replace('H ', '').replace('-','')
#                 list_of_lines.append(sentence)



# print(re.findall('(?<=\d.)[A-Za-z\s\-]*', descrepancy_string))
