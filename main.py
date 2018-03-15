from py2neo import Graph,Node,Relationship
import re

node_dict= dict()
graph=Graph("http://127.0.0.1:7474",username="neo4j",password="xlsd1996")

def delete_relation(line):
    pa = re.compile(":[^(]+")
    res = pa.sub('',line)
    return res

def merge_to_lines(file):
    lines = []
    res = ""
    for line in file:
        if(line[0]=="#" and len(res)>0):
            lines.append(res)
            res = ""
        if(line[0]!="#"):
            res+=line.strip()
    lines.append(res)
    return lines


def merge_to_one_line(file):
    res=""
    for line in file:
        if(line[0]=="#"):
            continue
        res+=line.strip()
    return res

def pop_node(stack):
    res = ""
    for i,c in enumerate(stack[::-1]):
        res+=c
        if(c=="("):
            return res[::-1],stack[:-1*(i+1)]
# a,r,b
#pop r and b
def pop_relationship(stack):
    res = ""
    q_count = 0
    slice_position = 0
    for i,c in enumerate(stack[::-1]):
        res+=c
        if(c==":"):
            slice_position = i
        if(c=="("):
            q_count+=1
            if(q_count==2):
                return res[::-1],stack[:-1*(slice_position+1)]

def save_node_to_dict(node):
    try:
        key = node[1:node.index(" ")]
        value = node[node.index("/")+2:-1]
        node_dict[key]=value
    except Exception as e:
        print(e)
        print("="*20)
        print(node)
        print("="*20)

def get_node_from_line(line):
    stack = ""
    i=0
    while(i<len(line)):
        stack+=line[i]
        if(line[i]==")"):
            node,stack=pop_node(stack)
            save_node_to_dict(node)
        i+=1

def get_all_nodes(line):
    line = delete_relation(line)
    get_node_from_line(line)
    # print(len(node_dict.items()))

def get_all_relationship(line):
    stack = ""
    i=0
    while(i<len(line)):
        stack+=line[i]
        if(line[i]==")"):
            if(':' in stack):
                r,stack=pop_relationship(stack)
                # print(r+")")
                create_one_relationship(r)
            else:
                stack=""
        i+=1

def create_node():
    for one in node_dict:
        graph.run("create ( n:Word {code:'%s',content:'%s'})"%(one,node_dict[one]))

def create_one_relationship(r):
    # cypher = ""
    a = r[1:r.index(' ')]
    try:
        agro=r[r.index(':')+1:r.find(' ', r.index(':')+1)]
        b = r[r.index(' (')+2:r.find(' /', r.index(' (')+1)]
        # print("%s-(%s)->%s" % (a, agro, b))
        # graph.create(Relationship(a, agro, b))
    except Exception as e:
        print(e)
        print("="*10)
        print(r)
        print("="*10)

def my_find_all(s,sub_str):
    return [m.start() for m in re.finditer(sub_str, s)]

def find_father_node_code(line,position):
    i = position-1
    count = 0
    while(i>=0):
        c = line[i]
        if(c==')'):
            count-=1
        elif(c=='('):
            count+=1
            if(count>0):
                code = re.findall("\((\w+) /",line[i:position])[0]
                return code
        i-=1

def filter_all_exception(line):
    pa = re.compile(":\S+ [^):(]+")
    es = set(re.findall(pa,line))
    for e in es:
        for p in my_find_all(line,e):
            father_code = find_father_node_code(line,p)
            print(father_code,e)
    res = pa.sub('',line)
    return res
if __name__ == "__main__":
    import sys
    if(len(sys.argv)!=2):
        print("run this script with one parameter: filename")
        exit()
    filename = sys.argv[1]
    with open(filename) as file:
        for l in merge_to_lines(file=file):
            line = filter_all_exception(line=l)
            get_all_nodes(line)
            get_all_relationship(line)
        #create_node()
