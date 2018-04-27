# coding=utf-8
from flask import Flask, jsonify, render_template, request
from py2neo import Graph,remote

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
def get_graph():
    words = request.args.get("words")
    words_list = words.split(' ')
    nodes = []
    edges = []
    max_size = 20
    # for word in words_list:
    #     qs = 'MATCH (n:Word) where n.content =~ "%s" RETURN n' % word
    #     for i in graph.run(qs):
    #         for n in get_all_related_nodes(i['n']['line_id']):
    #             node ={"id":get_node_id(n['n']),"code":n['n']['code'],"content":n['n']['content'],"line_id":n['n']['line_id']}
    #             nodes.append({"data":node})
    #             for e in get_all_relationship_by_line_id(line_id=n['n']['line_id']):
    #                 edge={"source":get_node_id(e['r'].start_node()),
    #                       "target":get_node_id(e['r'].end_node()),
    #                       "type":e['r']["type"]
    #                       }
    #                 edges.append({"data":edge})
    #         break
    for word in words_list:
        #TODO: the word must be safe
        qs = 'MATCH (n:Word) where n.content =~ ".*%s.*" RETURN n' % word
        for i in graph.run(qs):
            for n in get_nodes_by_line_id(i['n']['line_id']):
                node = {
                    "id": get_node_id(n['n']),
                    "label": n['n']['code'],
                    "code": n['n']['code'],
                    "content": n['n']['content'],
                    "line_id": n['n']['line_id']
                }
                nodes.append(node)
            for e in get_relationships_by_line_id(
                    line_id=n['n']['line_id']):
                edge = {
                    "source": get_node_id(e['r'].start_node()),
                    "target": get_node_id(e['r'].end_node()),
                    "type": e['r']["type"],
                }
                edges.append(edge)
            break

    #nodes = map(buildNodes, graph.run('MATCH (n) RETURN n limit 25'))
    # edges = map(buildEdges, graph.run('MATCH ()-[r]->() RETURN r limit 25'))
    res = jsonify({"nodes": nodes, "links": edges})
    return res


if __name__ == '__main__':
    app.run(debug=True)
