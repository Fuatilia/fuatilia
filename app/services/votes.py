import os
import io
from pypdf import PdfReader
import re

class PDF_Reader():
    '''
    path : string containing the path/url to the actual document
    path_type : web_url, s3_url, local(default)
    encoding : UTF-8 etc allows for multiplatform reads
        - You cans specify another encoding for a different file type/platform
    '''
    def __init__(self, path:str, path_type:str|None = None, encoding: str|None = None):
        self.path = path
        self.path_type = path_type
        self.encoding = encoding or 'utf-8' 
    
    def read_from_local(self)->PdfReader:
        print("Initiating read_from_local.")

        os_path = os.path.join(os.path.expanduser('~'), self.path)
        # Incase the file is not text readable retrun the binary
        file = open(os_path, "rb")
        print("File name ", file.name)
        f = file.read()
        f_stream = io.BytesIO(f)

        reader = PdfReader(f_stream)
        print("PDF page count : ",reader.get_num_pages(),"\n>>> Metadata : ", reader.metadata)
        file.close()
        return reader

    def read_from_s3_url(self):
        raise NotImplemented
        

    def read_from_web_url(self):
        raise NotImplemented
        

    def read_from_google_drive(self):
        raise NotImplemented
        


class Vote_Processor():
    def  __init__(self, file:PdfReader) -> None:
        self.file_reader = file
        self.pages = self.file_reader.get_num_pages()

    '''
    page_limit -- Incase you need to set a page limit for the search 
    '''
    def get_individual_page_to_begin(self, bill_title:str , page_to_start: int = 0 , page_limit:int = None):
        # Incase the roll call and bill title are in seperate pages
        has_bill_title = False
        has_roll_call = False
        bill_title_page: None|int = None
        roll_call_page: None|int = None
        self.page_limit = page_limit or self.pages
        
        for page_num in range(page_to_start, self.page_limit):
            page = self.file_reader.pages[page_num]
            page_text = page.extract_text(extraction_mode='layout')

            # print(page_text)

            print('---------- Initiating bill vote lookup ---- ',page_num)
            list_of_lines = page_text.split('\n')
            for line in list_of_lines:
                if line.find(bill_title)!=-1:
                    has_bill_title = True
                    bill_title_page = page_num
                if line.find('Results of the Roll Call Vote')!=-1:
                    has_roll_call = True
                    roll_call_page = page_num

            
            print(has_bill_title , has_roll_call , bill_title_page , roll_call_page)
            if has_bill_title and has_roll_call and bill_title_page and roll_call_page:
                return bill_title_page, roll_call_page


    '''
    Will search for any sequence of pages that contain documents
    '''
    def extract_individual_votes(self , page_to_begin_extraction:int = 0):
        # Flag for preventing reversal of vote_to_check on intial loop
        ayes_check_initiated = False 
        noes_check_initiated = False 
        vote_to_check = None
        stop_ayes_check = False
        stop_noes_check = False

        # Dummy summary dict
        summary_dict = { }
        
        print(f"Vote extraction initated for  --> {self.pages} pages")
        for page_num in range(page_to_begin_extraction, self.pages):
            page = self.file_reader.pages[page_num]
            page_text = page.extract_text(extraction_mode='layout')

            print('---------- Initiating vote extraction for page ---- ',page_num)
            list_of_lines = page_text.split('\n')
            for line in list_of_lines:
                # If vote to check string is found again it means we are at the bottom/end of the search 
                if (line.find('AYES')!=-1 and vote_to_check == 'YES') and ayes_check_initiated:
                    vote_to_check = None
                    ayes_check_initiated = False
                    stop_ayes_check = True

                if  (line.find('NOES')!=-1 and vote_to_check == 'NO') and noes_check_initiated:
                    vote_to_check = None
                    noes_check_initiated = False
                    stop_noes_check = True


                # Check for a vote direction header AYES vs NOES
                if line.find('AYES')!=-1 and vote_to_check != 'YES' and not ayes_check_initiated and not stop_ayes_check:
                    vote_to_check = 'YES'
                    ayes_check_initiated = True
                    # print("passes here")

                if line.find('NOES')!=-1 and vote_to_check != 'NO' and not noes_check_initiated and not stop_noes_check:
                    vote_to_check = 'NO'
                    noes_check_initiated = True                
                
                
                # Only process lines if process has picked vote direction
                if vote_to_check:
                    found_vote = re.search("^[0-9]*.\s{4,}[A-Za-z]*\s{4,}[A-Za-z\.\s\,\']*.*", line)
                    
                    if found_vote:
                        representative = re.search('(?!.*  ).+', found_vote.group(0))
                        rep_area = re.search('(?<=\s)[^(0-9)\s{4,}].*(?<=\s{2})', found_vote.group(0))


                        if rep_area and representative: 
                            representative = representative.group(0).lstrip().rstrip()
                            rep_area = rep_area.group(0).lstrip().rstrip()

                            if rep_area.find('Ayes')!=-1 or rep_area=='Noes'!=-1:
                                # return when it gets to the summary section at the end of the bill
                                # TODO : Find a way to pick summary 
                                return summary_dict
                            

                            summary_dict [representative] = {
                                'area' : rep_area,
                                'vote' : vote_to_check
                            }
                        else:
                            print(f"Failed to process data for rep {representative} and area {rep_area}")

        return summary_dict
        

r = PDF_Reader('Downloads/Tuesday, February 20 ,2024 At 2.30pm (2).pdf')
reader = r.read_from_local()
title_page, vote_page = Vote_Processor(reader).get_page_to_begin('AFFORDABLE HOUSING', 3, 4)
print(Vote_Processor(reader).extract_individual_votes(title_page))