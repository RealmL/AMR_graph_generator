from py2neo import Graph,Node,Relationship

node_dict= dict()
graph=Graph("http://127.0.0.1:7474",username="neo4j",password="xlsd1996")

def delete_relation(line):
    res = ""
    i=0
    while(i<len(line)):
        if(line[i]==":"):
            while(line[i]!="("):
                i+=1
        res+=line[i]
        i+=1
    return res

def merge_to_one_line(file):
    res=""
    for line in file:
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
    key = node[1:node.index(" ")]
    value = node[node.index("/")+2:-1]
    node_dict[key]=value

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
    print(node_dict)

def get_all_relationship(line):
    stack = ""
    i=0
    while(i<len(line)):
        stack+=line[i]
        if(line[i]==")"):
            if(':' not in stack):
                break
            r,stack=pop_relationship(stack)
            print(r+")")
            create_one_relationship(r)
            
        i+=1

def create_node():
    for one in node_dict:
        graph.run("create ( n:Word {code:'%s',content:'%s'})"%(one,node_dict[one]))

def create_one_relationship(r):
    # cypher = ""
    a = r[1:r.index(' ')]
    # if r.count(':')>1:
    #     temp=r[r.index(':')+1:-1]
    #     for i in range(r.count(':')):
    #         if temp.find('(',temp.index(':'),temp.)
    #
    # else:
    agro=r[r.index(':')+1:r.find(' ', r.index(':')+1)]
    b = r[r.index(' (')+2:r.find(' /', r.index(' (')+1)]
    print("%s-(%s)->%s" % (a, agro, b))
    # graph.create(Relationship(a, agro, b))

if __name__ == "__main__":
    with open("C:\\Work\\senior\\AMR\\example.txt") as file:
        line = merge_to_one_line(file)
        print(line)
        get_all_nodes(line)
        get_all_relationship(line)
        #create_node()
