import numpy as np
import collections

def scrape_text_13f(data):
    table_data = get_table(data).upper()
    data = table_data.split('\n')
    cat_tag_loc, val_tag_loc, title_loc, val_dash_loc, cat_dash_loc = parse_data_for_locations(data)
    max_loc = max(cat_tag_loc, val_tag_loc, title_loc, val_dash_loc, cat_dash_loc)
    print cat_tag_loc

    #EXAMPLES 1, 2
    if val_dash_loc:
        format_line = get_dash_format_line(data[val_dash_loc].strip())
        parsed_lines = parse_12(format_line, data[max_loc+1:])
    #Example3
    elif val_tag_loc:
        format_line = get_tag_format_line(data[val_tag_loc].strip())
        parsed_lines = parse_12(format_line, data[max_loc+1:])
    #Example4
    elif cat_tag_loc:
        format_line = get_tag_format_line(data[cat_tag_loc].strip())
        parsed_lines = parse_8(format_line, data[max_loc+1:])
    else:
        print 'BAD FORMAT'
        return None

    final_lines = clean_lines(parsed_lines)

    print 'FINAL LINES: '
    for x in final_lines:
        print x

def parse_data_for_locations(data):
    cat_tag_loc, val_tag_loc, title_loc, val_dash_loc, cat_dash_loc = None, None, None, None, None
    for ind, line in enumerate(data):
        line = line.strip().lower()
        if line.startswith('<s>'):
            if len(line.split()) == 12:
                val_tag_loc= ind
            elif len(line.split()) == 8:
                cat_tag_loc = ind
        elif line.startswith('--'):
            if len(line.split(' ')) == 8:
                cat_dash_loc = ind
            elif len(line.split(' ')) == 12:
                val_dash_loc = ind
        elif line.startswith('name of issuer'):
            title_loc = ind
    return cat_tag_loc, val_tag_loc, title_loc, val_dash_loc, cat_dash_loc

def get_tag_format_line(line):
    format_inds = []
    while True:
        ind = line.find('<')
        if ind < 0:
            break
        format_inds.append(ind+1)
        line = line[ind+1:]
    return list(np.cumsum([format_inds]))

def get_dash_format_line(line):
    format_inds = [0]+[len(x)+1 for x in line.split()]
    return list(np.cumsum([format_inds[:-1]]))

def get_table(data):
    text_data = ' '.join(data)
    return text_data.split('<TABLE>')[1].split('</TABLE>')[0]

def parse_8(format_line, lines):
    #split 5,6,7
    lines = [[lines[x][i:j].strip() for i,j in zip(format_line, format_line[1:]+[None])] for x in xrange(len(lines))]
    lines = map(expand_8_line, lines)
    return lines

def expand_8_line(line):
    print 'line', line
#Handles empty line
    if not ''.join(line):
        return line
    elif (line[5].split()[0] in ['SH','PRN']): 
        if line[5] not in ['SH','PRN']: line[5] = line[5].split()
        else: line[5] = [line[5]] + ['']
    elif line[5] in ['PUT','CALL']:
        line[5] = ['']+[line[5]]
        print line[5]
    line[6] = [line[6]] + ['']
    line[7] = line[7].split() + (3-len(line[7].split()))*['']
    return flatten(line)

def flatten(x):
    if isinstance(x, collections.Iterable) and not isinstance(x, basestring):
        return [a for i in x for a in flatten(i)]
    else:
        return [x]

def parse_12(format_line, lines):
    return [[lines[x][i:j].strip() for i,j in zip(format_line, format_line[1:]+[None])] for x in xrange(len(lines))]

def clean_lines(parsed_lines):
    print 'DROPPED LINES: '
    final_lines = []
    previous_line = []
    combine_lines = False
    for line in parsed_lines:
#combines extra on top lines
        if not validate_line_format(line):
            print 'INVALID LINE FORMAT', line
            continue
        if combine_lines:
            print zip(previous_line, line)
            hold_line = [' '.join(x).strip() for x in zip(previous_line, line)]
            print hold_line
            final_lines.append(hold_line)
            previous_line = None
            combine_lines = False
#delete empty lines
        elif len(''.join(line)) == 0:
            print line
            previous_line = None
            continue
#handle combining next line
        elif len([x for x in line if x]) < 7:
            #*Check if above line is valid or not
            previous_line = line
            combine_lines = True
#Delete Dash only line
        elif len(''.join(line).replace('-','')) == 0:
            print line
            previous_line = None
            continue
        else:
            final_lines.append(line)
    return final_lines

def validate_line_format(line):
    if len(line[2]) not in (7,8,9): return
    elif not line[3].replace(',','').isdigit(): return
    elif not line[4].replace(',','').isdigit(): return

    if len(line) == 12:
        if line[5] not in ('PRN','SH', ''): return
        elif line[6] not in ('PUT','CALL',''): return
        #elif line[7]:
        #elif line[8]:
        elif line[9] and not line[9].replace(',','').isdigit(): return
        elif line[10] and not line[10].replace(',','').isdigit(): return
        elif line[11] and not line[11].replace(',','').isdigit(): return
        else: return line

if __name__ == '__main__':
    file_base = 'ExampleFiles/'
    #for text_file in ['example2.txt', 'example3.txt', 'example5.txt']:
    #for text_file in ['example5.txt']:
    for text_file in ['example4.txt']:
        print text_file 
        with open(file_base + text_file) as f:
            data = f.readlines()
        scrape_text_13f(data)
