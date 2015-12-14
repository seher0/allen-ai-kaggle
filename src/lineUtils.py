def enlarge_window (sents, num):
    #return sents
    res = []
    for i, sent in enumerate(sents):
        curr = []
        for j in range (i-num, i+num+1):
            try:
                s = sents[j]
                curr.extend(s)
                
            except:
                pass
        res.append(curr)

    return res


sents = [
'i am a human being'.split(' '),
'he is not listening'.split(' '),
'where is the ball'.split(' ')

]

def mergeBrokenLines (lines):
    res = []
    curr = ''
    for line in lines:
        line = line.strip()
        if 'BY' in line:
            continue
        elif 'FIGURE' in line:
            continue

        curr = curr + ' ' + line
        if line.endswith('.'):
            res.append(curr)
            curr = ''
        elif '.' in line:
            print 'unwanted dot in middle'
            print line
            if line.replace('-','').replace(',','').replace('.','').replace(" ", '').isdigit():
                print '---removing'
                curr = ''
            if len(line) < 20:
                res.append(curr)
                curr = ''

    return res

def mergeBrokenFile (fname):
    with open(fname) as rf:
        outfname = fname + '.merged'
        print outfname
        lines = rf.readlines()
        lines = mergeBrokenLines(lines)
        with open(outfname, 'w') as of:
            of.write('\n'.join(lines) )


mergeBrokenFile ('../data/ck12foundation.txt')
mergeBrokenFile ('../data/ohio8grade-science.txt')
mergeBrokenFile ('../data/ck12-ls.txt')
mergeBrokenFile ('../data/ck12-ls-concepts.txt')
mergeBrokenFile ('../data/ck12-ps.txt')
mergeBrokenFile ('../data/ck12-ps-concepts.txt')

