import numpy as np



def scrape_text_13f(data):
    text_data = ' '.join(data)
    text_data = text_data.split('<TABLE>')[1].split('</TABLE>')[0]
    col_ind = text_data.find('<S>')
    text_lines = [x.strip() for x in text_data[col_ind:].strip().split('\n')]
    format_line = text_lines[0]
    print text_lines[0]
    print text_lines[1]
    lines = text_lines[1:]
    format_inds = [0]
    format_line = format_line[1:]

    while True:
        ind = format_line.find('<')
        if ind < 0:
            break
        format_inds.append(ind+1)
        format_line = format_line[ind+1:]

    format_line = list(np.cumsum([format_inds]))
    parsed_lines = [[lines[x][i:j].strip() for i,j in zip(format_line, format_line[1:]+[None])] for x in xrange(len(lines))]

    for x in parsed_lines:
        print x





if __name__ == '__main__':
    with open('0000919574-10-004879.txt') as f:
        data = f.readlines()
    scrape_text_13f(data)
