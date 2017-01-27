import numpy as np
import collections


VALID_SH_PRN = ('SH', 'PRN', '')
VALID_PUT_CALL = ('PUT', 'CALL', '')

def scrape_text_13f(data):
    table_data = get_table(data).upper()
    data = table_data.split('\n')
    cat_tag_loc, val_tag_loc, title_loc, val_dash_loc, cat_dash_loc = parse_data_for_locations(data)
    max_loc = max(cat_tag_loc, val_tag_loc, title_loc, val_dash_loc, cat_dash_loc)

    print val_tag_loc, val_dash_loc

    #EXAMPLES 1, 2
    if val_dash_loc:
        print 'USING VALUE DASHES'
        format_line = get_dash_format_line(data[val_dash_loc].strip())
        parsed_lines = parse_12(format_line, data[max_loc+1:])
    #Example3
    elif val_tag_loc:
        print 'USING VALUE TAGS'
        format_line = get_tag_format_line(data[val_tag_loc].strip())
        parsed_lines = parse_12(format_line, data[max_loc+1:])
    #Example4
    elif cat_tag_loc:
        format_line = get_tag_format_line(data[cat_tag_loc].strip())
        parsed_lines = parse_8(format_line, data[max_loc+1:])
    else:
        #parsed_lines = [[s.strip() for s in x.split('  ') if s.strip()] for x in data] 
        print 'BAD FORMAT'
        return None

    cleaned_lines = clean_lines(parsed_lines)
    final_lines = drop_invalid_lines(cleaned_lines)

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
            if len(line.split()) == 8:
                cat_dash_loc = ind
            elif len(line.split()) == 12:
                val_dash_loc = ind
        elif line.startswith('name of issuer'):
            title_loc = ind
    return cat_tag_loc, val_tag_loc, title_loc, val_dash_loc, cat_dash_loc

def get_tag_format_line(line):
    format_inds = []
    while True:
        ind = line.find('<')
        if ind < 0: break
        format_inds.append(ind+1)
        line = line[ind+1:]
    return list(np.cumsum([format_inds]))

def get_dash_format_line(line):
    format_inds = [0]
    while True:
        ind = line.find(' -')
        if ind < 0: break
        format_inds.append(ind+1)
        line = line[ind+1:]
    return list(np.cumsum([format_inds]))

#def get_dash_format_line(line):
#    format_inds = [0]+[len(x)+1 for x in line.split()]
#    return list(np.cumsum([format_inds[:-1]]))

def get_table(data):
    text_data = ' '.join(data)
    return text_data.split('<TABLE>')[1].split('</TABLE>')[0]

def parse_8(format_line, lines):
    #split 5,6,7
    lines = [[lines[x][i:j].strip() for i,j in zip(format_line, format_line[1:]+[None])] for x in xrange(len(lines))]
    lines = map(expand_8_line, lines)
    return lines

def expand_8_line(line):
#Handles empty line
    print line
    if not ''.join(line):
        return line
    if not line[5]: line[5] = ['']*2
    elif (line[5].split()[0] in VALID_SH_PRN): 
        if line[5] not in VALID_SH_PRN: line[5] = line[5].split()
        else: line[5] = [line[5]] + ['']
    elif line[5] in VALID_PUT_CALL:
        line[5] = ['']+[line[5]]
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
    #print 'DROPPED LINES: '
    final_lines = []
    previous_line = []
    combine_lines = False
    for line in parsed_lines:
#combines extra on top lines
        #if not validate_line_format(line):
        #    print 'INVALID LINE FORMAT', line
        #    continue
        if combine_lines:
            line = [' '.join(x).strip() for x in zip(previous_line, line)]
            #if len([x for x in hold_line if x]) < 7:

            #final_lines.append(hold_line)
            previous_line = None
            combine_lines = False

#delete empty lines
        if len(''.join(line)) == 0:
            print line
            combine_lines = False
            previous_line = None
            continue
#handle combining next line
        elif len([x for x in line if x]) < 5 and len(''.join(line).replace('-','')) > 0:
            #*Check if above line is valid or not
            if previous_line:
                line = [' '.join(x).strip() for x in zip(previous_line, line)]
                previous_line = line
                final_lines[-1] = line
            else:
                previous_line = line
                combine_lines = True
#Delete Dash only line
        elif len(''.join(line).replace('-','')) == 0:
            print line
            previous_line = None
            continue
        else:
            previous_line = line
            final_lines.append(line)
            combine_lines = False
    return final_lines

def drop_invalid_lines(cleaned_lines):
    final_lines = []
    for line in cleaned_lines:
        if not validate_line_format(line):
            print 'INVALID LINE FORMAT', line
            continue
        final_lines.append(line)
    return final_lines


def validate_line_format(line):
    errors = 0
    print line
    if not line or len(line) < 12: return
    if not line[0]: errors += 1
    if not line[1]: errors += 1
    if len(line[2]) not in (7,8,9): errors+=1
    if not line[3].replace(',','').isdigit(): errors+=1
    if not line[4].replace(',','').isdigit(): errors+=1

    if len(line) == 12:
        if line[5] not in VALID_SH_PRN: errors+=1
        if line[6] not in VALID_PUT_CALL: errors+=1
        if line[7].replace(',','').isdigit(): errors += 2
        if line[7].replace(',','').isdigit(): errors += 2
        #if line[8]:
        if line[9] and not line[9].replace(',','').isdigit(): errors+=1
        if line[10] and not line[10].replace(',','').isdigit(): errors+=1
        if line[11] and not line[11].replace(',','').isdigit(): errors+=1
    if errors == 0:
        return line
    if errors == 1:
        print 'PASSING WITH {} ERRORS: '.format(errors)
        print line
        return line
    else:
        print 'FAILING WITH {} ERRORS: '.format(errors)
        print line
        return

if __name__ == '__main__':
    file_base = 'ExampleFiles/'
    #for text_file in ['example1.txt', 'example2.txt', 'example3.txt', 'example4.txt','example5.txt', 'example7.txt','example8.txt']:
    for text_file in ['example10.txt']:
        print text_file 
        with open(file_base + text_file) as f:
            data = f.readlines()
        scrape_text_13f(data)


#EXAMPLE 7 
    # FAILING ON LAST COLUMN FORMAT
    # BAD COLUMN 5 SO MISFORMATTED

