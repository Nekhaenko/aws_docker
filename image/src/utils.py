import json
import re, os
import pandas as pd


COLUMN_REGEXP = re.compile(r'(?<=(?<=^)|(?<=\|))([^\|]+)(?=\|)')

with open('config.json') as f:
    config = json.load(f)
    
lloyds_head = config['lloyds_head']
keywords = config['keywords']
keywords = [i.lower() for i in keywords]

def clean_lloyds(pth):
    ignore = [{'', ' Description', 'Date', '.', ' Money Out (ВЈ)', ' Money In (ВЈ)', ' Balance (ВЈ)', ' .\n', 'Type', ' .'},
          {'Description\n'}, {'', 'Date', ' Money Out (ВЈ)', 'Type', ' Balance (ВЈ)\n'},
          {'Money In (ВЈ)\n'}, {'', '.', ' .', ' .\n'}, {'.\n'},
          {'', ' Description', 'Balance (ВЈ)', 'Date', '.', '.\n', ' Money Out (ВЈ)', ' Type', ' .', 'Money In (ВЈ)'},
          {'', 'Description\n'}, {'', ' Money Out (ВЈ)\n'}, {'', 'blank.\n'},
          {'', 'Balance (ВЈ)\n', 'Date', ' Money In (ВЈ)', 'Type'}, {'', '.', '.\n'},
          {'', 'Balance (ВЈ)\n', 'Date', ' Money In (ВЈ)', ' Type', 'Description'},
          {'', 'Date', ' Money Out (ВЈ)', ' Type', ' Balance (ВЈ)\n', 'Description'},
          {'', ' Money In (ВЈ)\n'}, {'', ' .\n'}
         ]
    
    with open(pth, 'r') as file:
        lines = file.readlines()

    with open(pth, 'w') as file:
        for line in lines:
            if line.strip():
                file.write(line)


    with open(pth, 'r') as file:
        lines = file.readlines()

    with open(pth, 'w') as file:
        for line in lines:
            line_spl = set(line.split('  '))
            
            if line_spl not in ignore:
                file.write(line)
                
    with open(pth, 'r') as file:
        lines = file.readlines()
        for k, ln in enumerate(lines):
            if ln.find('Column')>=0:
                start = k
            if ln.find('Transaction types')>=0:
                end = k
    with open(pth, 'w') as file:
        file.writelines([lloyds_head+'\n'] + lines[start + 1:end])


def spl_text(line):
    date = re.findall(r'^\b\d{2}−\d{2}−\d{4}\b', line)
    
    if len(date) > 0:
        date = date[0]
        pos = line.find(date) + len(date)
        return [line[:pos], line[pos:]]
    else:
        return ['', '']


def find_line(file_path):
    with open(file_path,  errors='ignore') as file:
        for num, line in enumerate(file, start=1):
            key_count = 0
            
            line = re.findall(r'[a-z]{2,}', line.lower())
            if 'date' in line :
                for ki in keywords:
                    if ki in line :
                        key_count += 1
                        if key_count > 2:
                            return num
                        
    allrows = get_report_info(file_path, 0, [''])
    for k, ln in enumerate(allrows[:round(len(allrows)*0.75)]):
        count = [1 for i in ln if len(i) > 0]
        count = sum(count)

        line = ''.join(ln)
        digits = re.findall(r'\d', line)
        if len(ln) == count and len(digits) == 0:
            # print('find line -2-')
            return k+1

    return None


def another_staf(all_lines: list) -> (list):
    max_len = max([len(i) for i in all_lines]) + 1

    # for idx, line in enumerate(all_lines):
    #     pre_string = re.sub(r'(?<=[^ ]) (?=[^ ])', '_', line)
    #     all_lines[idx] = pre_string.replace('_Year_', ' Year_')

    for idx, line in enumerate(all_lines):
        all_lines[idx] = line.replace(' ', '|')

    for idx, line in enumerate(all_lines):
        if len(line) < max_len:
            diff_len = max_len - len(line)
            all_lines[idx] += '|' * diff_len

    return all_lines, max_len



def detect_rows(all_lines):
    curr_border = False
    dict_rows = defaultdict(list)
    row_border_indexes = []
    row_idx = 0

    for line_idx, line in enumerate(all_lines):

        prev_border = curr_border

        if line.replace('|', '').strip():
            dict_rows[row_idx].append(line_idx)
            curr_border = False
        else:
            curr_border = True
            if not prev_border:
                row_border_indexes.append(line_idx)
            row_idx += 1

    return row_border_indexes, dict_rows


def detect_colums(all_lines: list) -> list:
    border_indexes = []
    curr_border = False
    for_delete = []
    len_all_lines = len(all_lines)
    zindex = 0

    for i in zip(*all_lines):

        prev_border = curr_border

        if '|' * len_all_lines == ''.join(i):
            curr_border = True
        else:
            curr_border = False

        if curr_border and prev_border:
            for_delete.append(zindex)
        elif curr_border and not prev_border:
            border_indexes.append(zindex)

        zindex += 1

    col_name_list = [[] for _ in range(len(border_indexes))]

    for bidx, bnum in enumerate(border_indexes):
        b_end_idx = bidx + 1

        if b_end_idx == len(border_indexes):
            b_end_num = None
        else:
            b_end_num = border_indexes[bidx + 1]

        for line in all_lines:
            col_name_list[bidx].append(line[bnum:b_end_num])

    colums = []

    for i in col_name_list:
        col_name = ' '.join(i).replace('|', '').strip().replace('_', ' ')
        colums.append(col_name)

    return colums


def get_all_col_coordinates(all_lines: list) -> (list, int):
    count_colums = []
    lines_with_coords = []

    for line in all_lines:
        coords = []

        for i in COLUMN_REGEXP.finditer(line):
            coords.append(i.span())

        count_colums.append(len(coords))
        lines_with_coords.append((coords, line))

    return lines_with_coords, max(count_colums)


def create_list_columns_shapes(
    lines_with_col_coord: list, max_columns: int, max_line_len: int
) -> list:
    min_max_pos = []
    result = []

    max_col_coords = [i for i in lines_with_col_coord if len(i) == max_columns]

    for col_idx in range(max_columns):
        min_max_pos.append(
            [
                min([j[col_idx][0] for j in max_col_coords]),
                max([j[col_idx][1] for j in max_col_coords]),
            ]
        )

    for line in lines_with_col_coord:
        for col_coords in line:
            for mmp in min_max_pos:
                if mmp[1] > col_coords[0]:
                    mmp[0] = min(mmp[0], col_coords[0])
                    break

    for col_idx in range(max_columns - 1):
        result.append((min_max_pos[col_idx][0], min_max_pos[col_idx + 1][0] - 1))

    result.append((min_max_pos[-1][0], max_line_len))

    return result


def get_sim_table(all_col_coords: list, table_col_shapes: list) -> list:
    table = []

    for c_cols, line in all_col_coords:
        row = [] + [''] * len(table_col_shapes)
        for i in c_cols:
            for idx_col, coords in enumerate(table_col_shapes):
                if coords[0] <= i[0] <= coords[1]:
                    row[idx_col] = line[i[0] : i[1]]

        table.append(row)

    return table


def get_report_info(path_to_txt_file: str, st_line, head_ln) -> list:
    all_lines = get_all_lines(path_to_txt_file, st_line, head_ln)
    if len(all_lines) > 2:
        for idx, line in enumerate(all_lines):
            all_lines[idx] = line.replace('\n', '')

        all_lines, max_line_len = another_staf(all_lines)

        # detect column coordinates
        all_col_coords, max_col_count = get_all_col_coordinates(all_lines)

        # create list of columns with start positions in there
        table_col_shapes = create_list_columns_shapes(
            [i[0] for i in all_col_coords], max_col_count, max_line_len
        )

        tru_table = get_sim_table(all_col_coords, table_col_shapes)

        return tru_table
    else:
        return []


def get_all_lines(path_to_txt_file: str, st_line, head_ln) -> list:
    try:
        with open(path_to_txt_file, encoding = 'utf-8') as f:
            all_lines = f.readlines()
            for idx, line in enumerate(all_lines):
                byte_line = line.encode('utf8')
                byte_line = byte_line.replace(b'\xe2\x80\x93', b'-')
                byte_line = byte_line.replace(b'\xe2\x80\x99', b'`')
                all_lines[idx] = byte_line.decode('utf8')
            if len(head_ln[0]) > 0:
                return  head_ln + all_lines[st_line:]
            else:
                return all_lines[st_line:]
    except:
        with open(path_to_txt_file, 'r', encoding='cp1250') as f:
            all_lines = f.readlines()
            if len(head_ln[0]) > 0:
                return  head_ln + all_lines[st_line:]
            else:
                return all_lines[st_line:]


def extract_table(path, num_line, head_ln):
    allrows = get_report_info(path, num_line, head_ln)
    if len(allrows) > 2:
        names = allrows[0]
        df = pd.DataFrame(columns=names)

        r=0
        for ia in allrows[1:]:
            q1=0
            end_bool = True
            a1 = len(ia)
            for i11 in ia[:-1]:
                if len(i11)==0:
                    q1 += 1
            if q1 == a1-1 and len(ia[a1-1])>0:
                end_bool = False

            ia1 = ''.join(ia)

            if len(ia1)>0 and end_bool:
                df.loc[r] = ia
                r += 1

        cols = df.columns.tolist()

        for col in cols:
            try:
                df[col] = df[col].str.replace('_', ' ')
            except:
                pass
            
        # len_df = round(len(df)/2)
        # last_5_rows = df.tail(len_df)
        # for index, row in last_5_rows.iterrows():
            
        #     part1 = [i for i in row[:2] if len(i) >= 25]
        #     part2 = [i for i in row[2:] if len(i) > 0]
        #     if (len(part1) > 0) and (len(part2) == 0):
        #         df.drop(df.index[index:], inplace=True)
        #         break    

        return df
    else:
        return pd.DataFrame()


def crtdir(root_dir, direct):
    path = os.path.join(root_dir[:-4], direct)
    path_fl = os.path.join(path, f'{direct}.xlsx')
    try:
        os.mkdir(path)
        return path_fl
    except FileExistsError:
        return path_fl
    

def lloyds(df):
    qnan = df.loc[0].tolist()[0]

    cols = df.columns
    df[cols[0]].fillna('---', inplace=True)
    ind = []
    for_remove = [{qnan, 'Description'},
                {qnan, '---', 'Description'},
                {qnan, '---'}, 
                {qnan, '---', 'Money In (£)'}, 
                {'.', qnan, '---'},
                {qnan}, {'Balance (£)', 'Date', 'Type', qnan}, 
                {'.', qnan}, {qnan},
                {'Balance (£)', 'Date', 'Description', 'Type', qnan}]

    for i in df.index:
        if set(df.loc[i]) in for_remove:
            ind.append(i)
            
        if 'Date' in set(df.loc[i]) or 'blank.' in set(df.loc[i]):
            ind.append(i)
        
        if len(df.loc[i, cols[0]])> 9:
            ind.append(i)
            
    df.drop(ind, axis=0, inplace=True)

    df.reset_index(inplace=True, drop=True)

    df.fillna('', inplace=True)

    ind = []
    for i in df.index:
        first_col = df.loc[i, cols[0]]
        first_col = re.findall('\d{2} \w{3} \d{2}', first_col)
        sc_col = df.loc[i, cols[1]]
        if len(first_col) > 0 and len(sc_col) == 0:
            df.loc[i, cols[1]] = df.loc[i-1,cols[1]] + ' ' + df.loc[i, cols[1]] + ' ' +df.loc[i+1,cols[1]]
            ind.append(i-1)
            ind.append(i+1)
        
    df.drop(ind, axis=0, inplace=True)
    df.drop_duplicates(inplace=True)
    return df