'''
Created on 29 Dec 2021

@author: Tinka
'''
from re import findall
from pathlib import Path

class HtmlTemplate(object):
    '''
    classdocs
    '''


    def __init__(self, filename, previous=None):
        '''
        Constructor
        '''
        self.filename = filename + ".html"
        self.previous = previous
        if previous is None:
            self.previous = dict()
        escape = '#'
        ### print(__file__)
        p = Path(__file__).parent
        filename = p.joinpath(self.filename)
        ### print(filename)
        with open(filename) as template:
            everything = template.readlines() # read all the lines
            everything = ''.join(everything) # and put them back together

        self.parts = []
        # gather the template parts
        while len(everything) > 0:
            left = ''
            insert = None
            right = ''
            # look for the escape character
            pos = everything.find(escape)
            if pos < 0: # not found so only have text left ...
                left = everything
                everything = ''
            else:
                # create the text part
                left = everything[:pos]
                everything = everything[pos + 1:]
                if everything.startswith(escape):
                    # is escaped escape, so add to text and skip on
                    left += escape
                    everything = everything[1:]
                else:
                    # some insert, so find its end
                    pos = everything.find(escape)
                    if pos < 0: # not found so actually an error!, but treat it as end of the insert
                        right = everything
                        everything = ''
                    else:
                        right = everything[:pos]
                        everything = everything[pos + 1:]
                    # here with left as any text, and right as an insert
                    insert = findall(r"\w+", right) # convert to list of words
                # here with left and insert as words
            if len(left) > 0:
                self.parts.append(('t', left)) # add a text insert
            if insert is not None:
                self.parts.append((insert[0], insert[1:])) # use first word as type and rest as parameters
        return

    def getTemplate(self, contents):
        filename = contents[0]
        keys = contents[1:]
        if filename not in self.previous:
            template = HtmlTemplate(filename, self.previous)
            self.previous[filename] = template
        else:
            template = self.previous[filename]
        return template, keys

    def generate(self, **params):
        ### print("Generating:", self.filename, params)
        html = ''
        for insertType, contents in self.parts:
            if insertType == 't':
                html += contents
            else:
                # functional insert
                if insertType == 'insert':
                    # insert another template here ...
                    template, keys = self.getTemplate(contents)
                    ### print("Processing insert:", contents[0], "with:", keys)
                    newParams = dict()
                    for key in keys: # use keywords passed in for call
                        newParams[key] = params.get(key, None)
                    html += template.generate(**newParams)
                elif insertType == 'if':
                    # like insert, but only do if first parameter is not blank
                    template, keys = self.getTemplate(contents)
                    test = keys[0] # first is test parameter
                    keys = keys[1:] # rest as before
                    ### print("Processing if:", contents[0], "test:'" + test + "'", "with:", keys)
                    if "" != params.get(test, ""):
                        newParams = dict()
                        for key in keys: # use keywords passed in for call
                            newParams[key] = params.get(key, None)
                        html += template.generate(**newParams)
                    # if blank skipping
                elif insertType == 'iterate':
                    # like insert, but iterate over parameters
                    template, keys = self.getTemplate(contents)
                    ### print("Processing iterate:", contents[0], "with:", keys)
                    runOut = False
                    index = 0
                    while not runOut:
                        newParams = dict()
                        runOut = True # assume false unless we find an iteration to use
                        for key in keys: # use keywords passed in for call
                            param = params.get(key, None)
                            ### print("Index:", index, "- Key:", key, "- param:", param)
                            if param is not None:
                                if isinstance(param, (list, tuple, range)):
                                    if index < len(param):
                                        newParams[key] = param[index]
                                        runOut = False # ok, we have an iteration, so keep going
                                else:
                                    newParams[key] = param
                        ### print("newParams:", newParams)
                        ### print("Index:", index, "- runOut:", runOut, ", param len:", len(newParams))
                        if not runOut and (len(newParams) > 0):
                            html += template.generate(**newParams)
                        index += 1
                    # end while iterations
                else:
                    # must be a variable name
                    key = insertType # ignore all others
                    text = params.get(key, 'no param: ' + key) #'') # skip is not there
                    ### print("Processing:", key, "as", text)
                    html += text
                # end of functional inserts
            # end of text / non-text switch
        # done all parts
        return html
