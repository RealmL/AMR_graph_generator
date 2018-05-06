# coding=utf-8
from flask import Flask, jsonify, render_template, request
from py2neo import Graph, remote

app = Flask(__name__)
graph = Graph("http://127.0.0.1:7474", username="neo4j", password="xlsd1996")


# def buildNodes(nodeRecord):
#     data = {"id": str(nodeRecord.n._id), "content": next(iter(nodeRecord.n.content))}
#     data.update(nodeRecord.n.properties)
#
#     return {"data": data}

# def buildEdges(relationRecord):
#     data = {"source": str(relationRecord.r.start_node._id),
#             "target": str(relationRecord.r.end_node._id),
#             "relationship": relationRecord.r.rel.type}
#
#     return {"data": data}


@app.route('/')
def index():
    return render_template('index.html')


def get_node_id(node):
    id = remote(node)._id
    return id


def get_nodes_by_line_id(line_id):
    cypher = "MATCH (n:Word) where n.line_id ='%s' RETURN n" % (line_id)
    for node in graph.run(cypher):
        yield node


def get_relationships_by_line_id(line_id):
    cypher = "MATCH ()-[r]->() where r.line_id ='%s' RETURN r" % (line_id)
    for re in graph.run(cypher):
        yield re


@app.route('/graph')
def get_graph_by_lineid():
    line_id = request.args.get("line_id")
    nodes = []
    edges = []
    # get all nodes in target line
    for n in get_nodes_by_line_id(line_id):
        node = {
            "id": get_node_id(n['n']),
            "label": n['n']['code'],
            "code": n['n']['code'],
            "content": n['n']['content'],
            "line_id": n['n']['line_id']
        }
        nodes.append(node)
    # get all relation in target line
    for e in get_relationships_by_line_id(
            line_id=line_id):
        edge = {
            "source": get_node_id(e['r'].start_node()),
            "target": get_node_id(e['r'].end_node()),
            "type": e['r']["type"],
        }
        edges.append(edge)
    res = jsonify({"nodes": nodes, "links": edges})
    return res


@app.route('/snts')
def search_sentences_by_keywords():
    words = request.args.get("words")
    words_list = words.split(' ')

    res = []
    for word in words_list:
        cypher = "Match (s:Snt) Where s.content =~ '.*(?i)%s.*' Return s" % word
        if (not res):
            res = set(graph.run(cypher))
        else:
            temp = set(graph.run(cypher))
            res &= temp

    return jsonify([{"content": s['s']['content'], 'line_id': s['s']['line_id']} for s in res])


if __name__ == '__main__':
    app.run(debug=True)
