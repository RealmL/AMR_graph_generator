from py2neo import Graph,Node,Relationship
import re

node_dict= dict()
relationships = []

graph=Graph("http://127.0.0.1:7474",username="neo4j",password="xlsd1996")

def delete_relation(line):
    pa = re.compile(":[^(]+")
    res = pa.sub('',line)
    return res

def merge_to_lines(file):
    lines = []
    res = ""
    line_id = ""
    for line in file:
        if(line[0]=="#" and len(res)>0):
            lines.append((res,line_id))
            res = ""
        if(line[:6]=="# ::id"):
            line_id = re.findall("\# ::id (\S+) ::",line)[0]
        if(line[0]!="#"):
            res+=line.strip()
    lines.append((res,line_id))
    return lines

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

def save_node_to_db(node,line_id):
    #example: (o / obligate-01)
    code = node[1:node.index(' ')]
    content = node[node.index('/')+2:-1]
    create_node(code,content,line_id)
    print((code,content,line_id))

def get_node_from_line(line,line_id):
    stack = ""
    i=0
    while(i<len(line)):
        stack+=line[i]
        if(line[i]==")"):
            node,stack=pop_node(stack)
            save_node_to_db(node,line_id)
        i+=1

def get_all_nodes(line,line_id):
    line = delete_relation(line)
    get_node_from_line(line,line_id)

def get_all_relationship(line,line_id):
    stack = ""
    i=0
    while(i<len(line)):
        stack+=line[i]
        if(line[i]==")"):
            if(':' in stack):
                r,stack=pop_relationship(stack)
                # print(r+")")
                a=r[1:r.index(' ')]
                argo=r[r.index(':')+1:r.find(' ', r.index(':')+1)]
                b = r[r.index(' (')+2:r.find(' /', r.index(' (')+1)]
                t=(a,argo,b,line_id)
                relationships.append(t)
            else:
                stack=""
        i+=1

def create_node(code,content,line_id):
    graph.run("create ( n:Word {code:'%s',content:'%s',line_id:'%s'})" % (code,content,line_id))


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


def save_ex_relation(father_code,e,line_id):
    r,c = e.strip().split(' ')
    t = (father_code,r[1:],c,line_id)
    relationships.append(t)

def filter_all_exception(line,line_id):
    pa = re.compile(":\S+ [^):(]+")
    es = set(re.findall(pa,line))
    for e in es:
        for p in my_find_all(line,e):
            father_code = find_father_node_code(line,p)
            save_ex_relation(father_code,e,line_id)
    res = pa.sub('',line)
    return res

def save_all_relationships():
    for a,argo,b,line_id in relationships:
        print(( a,argo,b,line_id))
        b = b.replace("'"," ")
        cypher = "MATCH (a:Word {code:'%s',line_id:'%s'}),(b:Word {code:'%s',line_id:'%s'}) CREATE (a)-[:LINK {type:'%s'}]->(b)" % (a,line_id,b,line_id,argo)
        graph.run(cypher)

if __name__ == "__main__":
    import sys
    if(len(sys.argv)!=2):
        print("run this script with one parameter: filename")
        exit()
    filename = sys.argv[1]
    with open(filename) as file:
        for l,line_id in merge_to_lines(file=file):
            line = filter_all_exception(l,line_id)
            get_all_nodes(line,line_id)
            get_all_relationship(line,line_id)
    save_all_relationships()
        #create_node()
