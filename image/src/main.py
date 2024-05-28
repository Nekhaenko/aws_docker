import boto3
from utils import find_line, extract_table, spl_text, lloyds, clean_lloyds
import pandas as pd
import os, json

with open('config.json') as f:
    config = json.load(f)

file_path = 'txt'
HDFC_BANK = config['HDFC_BANK']

def main():
    for folderi in os.listdir(file_path):
        folderi = os.path.join(file_path, folderi)
        all_pages = pd.DataFrame()
        first_page = False
        head_line = ['']
        for k, fli in enumerate(os.listdir(folderi)):
            k += 1
            fli = os.path.join(folderi, f'{k}.txt')
            line_number = find_line(fli)

            with open(fli, errors='ignore') as txtfl:
                text_ = txtfl.read()
                if len(text_) < 100:
                    return 'Wrong pdf file'

            if text_.find('HDFC BANK LIMITED') > 0 and  line_number is None:
                with open(fli, errors='ignore') as txtfl:
                    txt_ln = txtfl.readlines()
                
                txt_ln[23] = HDFC_BANK
                with open(fli, 'w') as txt_wr:
                    txt_wr.writelines(txt_ln)

            if k == 1:
                with open(fli, errors='ignore') as txtfl:
                    text = txtfl.read()

                if text.find('Tran Id-1 UTR Number') > 0:
                    text = text.replace('Tran Id-1 UTR Number', 'Tran Id-1   UTR Number')
                    with open(fli, 'w') as txt_wr:
                        txt_wr.write(text)

            table = pd.DataFrame()

            if k == 3 and text.find('Lloyds Bank') > 0:
                clean_lloyds(fli)

            if not first_page:
                line_number = find_line(fli)

                if line_number:
                    table = extract_table(fli, line_number - 1, [''])
                    first_page = True
                
                    with open(fli, errors='ignore') as txtfl:
                        head_line = txtfl.readlines()
                        head_line = head_line[line_number-1]
            else:
                line_number = find_line(fli)
                if line_number is None:
                    table = extract_table(fli, 0, [head_line])
                else:
                    table = extract_table(fli, line_number - 1, [''])

            if len(table) > 0:
                if '' in table.columns:
                    table.drop('', axis = 1, inplace=True)
                if '.' in table.columns:
                    table.drop('.', axis = 1, inplace=True)

                all_pages = pd.concat([all_pages, table], ignore_index=True)
            
        if text.find('THE COSMOS') > 0:
            cols = all_pages.columns
            all_pages[cols[:2]] = all_pages[cols[0]].apply(spl_text).apply(pd.Series)

        if text.find('Lloyds Bank') > 0:
            all_pages = lloyds(all_pages)

        if len(all_pages) > 0:
            return all_pages.to_csv(index = False)
        else:
            return ''


df = main()