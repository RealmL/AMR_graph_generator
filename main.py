from py2neo import Graph,Node
import re

DEBUG_LEVEL = 1 #1 for db_info;2 for exception info ;3 for all info

nodes_dict = dict()
ex_nodes_dict = dict()
relationships = []

escape_dict = {
    '\a': r'\a',
    '\b': r'\b',
    '\c': r'\c',
    '\f': r'\f',
    '\n': r'\n',
    '\r': r'\r',
    '\t': r'\t',
    '\v': r'\v',
    '\'': r'\'',
    '\"': r'\"',
    '\0': r'\0',
    '\1': r'\1',
    '\2': r'\2',
    '\3': r'\3',
    '\4': r'\4',
    '\5': r'\5',
    '\6': r'\6',
    '\7': r'\7',
    '\8': r'\8',
    '\9': r'\9'
}


def raw(text):
    """Returns a raw string representation of text"""
    new_string = ''
    for char in text:
        try:
            new_string += escape_dict[char]
        except KeyError:
            new_string += char
    return new_string


graph = Graph("http://127.0.0.1:7474", username="neo4j", password="xlsd1996")


def delete_relation(line):
    pa = re.compile(":[^(]+")
    res = pa.sub('', line)
    return res


def merge_to_lines(file):
    lines = []
    res = ""
    line_id = ""
    snt = ""
    for line in file:
        if (line[0] == "#" and len(res) > 0):
            lines.append((res, line_id,snt))
            res = ""
        if (line[:6] == "# ::id"):
            line_id = re.findall("\# ::id (\S+) ::", line)[0]
        if("# ::snt" in line):
            snt = line[8:].strip()
        if (line[0] != "#"):
            res += line.strip()
    lines.append((res, line_id,snt))
    return lines


def pop_node(stack):
    res = ""
    for i, c in enumerate(stack[::-1]):
        res += c
        if (c == "("):
            return res[::-1], stack[:-1 * (i + 1)]


# a,r,b
#pop r and b
def pop_relationship(stack):
    res = ""
    q_count = 0
    slice_position = 0
    for i, c in enumerate(stack[::-1]):
        res += c
        if (c == ":"):
            slice_position = i
        if (c == "("):
            q_count += 1
            if (q_count == 2):
                return res[::-1], stack[:-1 * (slice_position + 1)]


def get_node_from_line(line):
    stack = ""
    i = 0
    while (i < len(line)):
        stack += line[i]
        if (line[i] == ")"):
            node, stack = pop_node(stack)
            yield node
        i += 1


def get_all_nodes(line, line_id):
    line = delete_relation(line)
    for node in get_node_from_line(line):
        code = node[1:node.index(' ')]
        content = node[node.index('/') + 2:-1]
        t = (code, content, line_id)
        if (DEBUG_LEVEL >= 3):
            print(t)
        nodes_dict[t[0]] = t

def get_all_relationship(line, line_id):
    stack = ""
    i = 0
    while (i < len(line)):
        stack += line[i]
        if (line[i] == ")"):
            if (':' in stack):
                r, stack = pop_relationship(stack)
                # print(r+")")
                a = r[1:r.index(' ')]
                argo = r[r.index(':') + 1:r.find(' ', r.index(':') + 1)]
                b = r[r.index(' (') + 2:r.find(' /', r.index(' (') + 1)]
                t = (a, argo, b, line_id)
                if (DEBUG_LEVEL >= 3):
                    print(t)
                relationships.append(t)
            else:
                stack = ""
        i += 1


def create_node(code, content, line_id):
    graph.run("create ( n:Word {code:'%s',content:'%s',line_id:'%s'})" %
              (code, content, line_id))

def my_find_all(s, sub_str):
    return [m.start() for m in re.finditer(sub_str, s)]


def find_father_node_code(line, position):
    i = position - 1
    count = 0
    while (i >= 0):
        c = line[i]
        if (c == ')'):
            count -= 1
        elif (c == '('):
            count += 1
            if (count > 0):
                code = re.findall("\((\w+) /", line[i:position])[0]
                return code
        i -= 1


def save_ex_relation(father_code, exception_piece, line_id):
    relationship, child = exception_piece.strip().split(' ')
    t = (father_code, relationship[1:], child, line_id)
    relationships.append(t)
    # print(t)

def exist_ex_node(code:str):
    return code in ex_nodes_dict

def exist_normal_node(code:str):
    return code in nodes_dict

def save_ex_node(exception_piece, line_id):
    relationship, child = exception_piece.strip().split(' ')
    t = (raw(child), raw(child), line_id)
    if(not exist_ex_node(t[0])):
        ex_nodes_dict[t[0]] = t
        # print(t)

def filter_all_exception(line, line_id):
    exception_parten = re.compile(":\S+ [^):(]+")
    exception_pieces = set(re.findall(exception_parten, line))
    for exception_piece in exception_pieces:
        for p in my_find_all(line, exception_piece):
            father_code = find_father_node_code(line, p)
            if (DEBUG_LEVEL >= 2):
                print((father_code, exception_piece))
            save_ex_relation(father_code, exception_piece, line_id)
        save_ex_node(exception_piece, line_id)
    res = exception_parten.sub('', line)
    return res


def save_all_nodes():
    for code in nodes_dict:
        code, content, line_id = nodes_dict[code]
        if (DEBUG_LEVEL == 1):
            print("Create node:",(code, content, line_id))
        create_node(code, content, line_id)
    for code in ex_nodes_dict:
        if(code not in nodes_dict):
            code, content, line_id = ex_nodes_dict[code]
            if (DEBUG_LEVEL == 1):
                print("Create node:", (code, content, line_id))
            create_node(code, content, line_id)
    nodes_dict.clear()
    ex_nodes_dict.clear()


def save_all_relationships():
    for a, argo, b, line_id in relationships:
        if (DEBUG_LEVEL == 1):
            print("Create relationship:",(a, argo, b, line_id))
        b = b.replace("'", " ")
        cypher = "MATCH (a:Word {code:'%s',line_id:'%s'}),(b:Word {code:'%s',line_id:'%s'}) CREATE (a)-[:LINK {type:'%s',line_id:'%s'}]->(b)" % (
            a, line_id, b, line_id, argo , line_id)
        graph.run(cypher)
    relationships.clear()

def save_sentence(snt,line_id):
    snt = Node("Snt",content=snt,line_id=line_id)
    # graph.run("create ( n:Snt {content:'%s',line_id:'%s'})" %
    #           (snt, line_id))
    graph.create(snt)

def remove_all():
    cypher = "match (n) where n:Word or n:Snt detach delete n;"
    graph.run(cypher)

if __name__ == "__main__":

    remove_all()

    import sys
    if (len(sys.argv) < 2):
        print("run this script with atleast one parameter: filename")
        exit()
    if(len(sys.argv)==3):
        DEBUG_LEVEL = int(sys.argv[2])
    filename = sys.argv[1]
    with open(filename) as file:
        for l,line_id,snt in merge_to_lines(file=file):
            save_sentence(snt,line_id)
            line = filter_all_exception(l, line_id)
            get_all_nodes(line, line_id)
            get_all_relationship(line, line_id)
            save_all_nodes()
            save_all_relationships()
            # print("="*20+"Nodes"+"="*20)
            # for code in nodes_dict:
            #     print(nodes_dict[code])
            # print("="*20+"Ex_Nodes"+"="*20)
            # for code in ex_nodes_dict:
            #     print(ex_nodes_dict[code])

