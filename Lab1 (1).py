import re
import sys
import collections
import random
import matplotlib.pyplot as plt
import networkx as nx

def preprocess_text(text):
    # 将文本中的标点符号替换为空格
    text = re.sub(r'[^\w\s]', ' ', text)
    # 将换行/回车符替换为空格
    text = text.replace('\n', ' ').replace('\r', ' ')
    return text.lower()

def build_graph(text):
    words = text.split()
    word_pairs = [(words[i], words[i+1]) for i in range(len(words)-1)]
    graph = nx.DiGraph()
    for pair in word_pairs:
        if pair not in graph.edges:
            graph.add_edge(pair[0], pair[1], weight=1)
        else:
            graph[pair[0]][pair[1]]['weight'] += 1
    return graph

def showDirectedGraph(graph, **kwargs):
    pos = nx.spring_layout(graph)
    plt.figure(figsize=(10, 8))  # 创建一个图形对象
    nx.draw_networkx(graph, pos, with_labels=True, node_color='skyblue', node_size=1500, edge_color='black',
                     linewidths=1, font_size=15)
    edge_labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)
    plt.show()

def queryBridgeWords(word1, word2, graph):
    if word1 not in graph.nodes and word2 in graph.nodes:
        return "No \"{}\" in the graph!".format(word1)

    if word2 not in graph.nodes and word1 in graph.nodes:
        return "No \"{}\" in the graph!".format(word1)

    if word1 not in graph.nodes and word2 not in graph.nodes:
        return "No \"{}\" and \"{}\" in the graph!".format(word1, word2)

    bridge_words = []
    for neighbor in graph.neighbors(word1):
        if graph.has_edge(neighbor, word2):
            bridge_words.append(neighbor)

    if not bridge_words:
        return "No bridge words from \"{}\" to \"{}\"!".format(word1, word2)
    elif len(bridge_words) == 1:
        return "The bridge words from \"{}\" to \"{}\" is: \"{}\".".format(word1, word2, ", ".join(bridge_words))
    else:
        return "The bridge words from \"{}\" to \"{}\" are: \"{}\".".format(word1, word2, ", ".join(bridge_words))

def insert_bridge_words(text, graph):
    text = preprocess_text(text)
    words = text.split()
    new_text = []
    for i in range(len(words) - 1):
        new_text.append(words[i])
        word1 = words[i]
        word2 = words[i+1]
        bridge_words = []
        if word1 not in graph or word2 not in graph:
            continue
        else:
            for neighbor in graph.neighbors(word1):
                if graph.has_edge(neighbor, word2):
                    bridge_words.append(neighbor)
            if bridge_words:
                bridge_word = random.choice(bridge_words)
                new_text.append(bridge_word)
    new_text.append(words[-1])
    return " ".join(new_text)

def calcShortestPath(word1, word2, graph):
    if word1 not in graph.nodes:
        return "No \"{}\" in the graph!".format(word1), [], 0

    if word2 not in graph.nodes:
        return "No \"{}\" in the graph!".format(word2), [], 0

    try:
        shortest_path = nx.shortest_path(graph, source=word1, target=word2, weight='weight')
        shortest_path_length = nx.shortest_path_length(graph, source=word1, target=word2, weight='weight')
        return shortest_path, shortest_path_length
    except nx.NetworkXNoPath:
        return "No path from \"{}\" to \"{}\" in the graph!".format(word1, word2), [], 0


def showShortestPath(graph, path):
    pos = nx.spring_layout(graph)
    plt.figure(figsize=(10, 8))
    nx.draw(graph, pos, with_labels=True, node_color='skyblue', node_size=1500, edge_color='black',
            linewidths=1, font_size=15)

    # Highlight the shortest path
    path_edges = list(zip(path, path[1:]))
    nx.draw_networkx_edges(graph, pos, edgelist=path_edges, edge_color='r', width=2)

    edge_labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

    plt.title("Graph with Shortest Path Highlighted")
    plt.show()

def randomWalk(graph):
    print("Press 'q' to stop the walk, or any other key to continue: ")
    current_node = random.choice(list(graph.nodes))
    visited_nodes = [current_node]
    visited_edges = []
    i = 0
    print(visited_nodes[i])

    while True:
        neighbors = list(graph.neighbors(current_node))
        if not neighbors:
            break
        next_node = random.choice(neighbors)
        visited_edges.append((current_node, next_node))
        visited_nodes.append(next_node)
        current_node = next_node
        i = i+1
        print(visited_nodes[i], end='')
        if has_duplicate(visited_edges):  # If we revisit a node, stop the walk
            break

        stop = input().lower()
        if stop == 'q':
            print(visited_nodes[-1])
            break

    # Write the visited nodes and edges to a text file
    with open("random_walk_result.txt", "w") as file:
        file.write("Visited nodes:\n")
        file.write(" -> ".join(visited_nodes))
        file.write("\n\nVisited edges:\n")
        for edge in visited_edges:
            file.write(f"{edge[0]} -> {edge[1]}\n")

    return "Random walk result has been saved to 'random_walk_result.txt'."

def has_duplicate(strings):
    return len(strings) != len(set(strings))

def main():
    file_path = input("Enter file path: ").strip()
    try:
        with open(file_path, 'r') as file:
            text = file.read()
            processed_text = preprocess_text(text)
            graph = build_graph(processed_text)
            while True:
                print("\n1. Show Directed Graph")
                print("2. Query Bridge Words")
                print("3. Insert Bridge Words into New Text")
                print("4. Calculate Shortest Path")
                print("5. RandomWalk")
                print("6. Exit")
                choice = input("Enter your choice (1/2/3/4/5/6): ").strip()
                if choice == '1':
                    showDirectedGraph(graph, with_labels=True, node_color='skyblue', node_size=1500, edge_color='black', linewidths=1, font_size=15)
                elif choice == '2':
                    word1 = input("Enter word1: ").strip().lower()
                    word2 = input("Enter word2: ").strip().lower()
                    result = queryBridgeWords(word1, word2, graph)
                    print(result)
                elif choice == '3':
                    new_text = input("Enter new text: ").strip().lower()
                    result = insert_bridge_words(new_text, graph)
                    print("New text with inserted bridge words:")
                    print(result)
                elif choice == '4':
                    word1 = input("Enter word1: ").strip().lower()
                    word2 = input("Enter word2: ").strip().lower()
                    if word2 == ".":
                        for target in graph.nodes:
                            if target == word1:
                                continue
                            result, length = calcShortestPath(word1, target, graph)
                            '''
                            if isinstance(result, str):
                                continue
                            '''
                            print(" -> ".join(result))
                    else:
                        result, length = calcShortestPath(word1, word2, graph)
                        if isinstance(result, str) :
                            print("Shortest path from \"{}\" to \"{}\":".format(word1, word2))
                            print(" -> ".join(result))
                            print("Length of shortest path:", length)
                            showShortestPath(graph, result)
                        else:
                            print(" -> ".join(result))
                            showShortestPath(graph, result)
                elif choice == '5':
                    print(randomWalk(graph))
                elif choice == '6':
                    print("Exiting...")
                    break
                else:
                    print("Invalid choice! Please enter 1, 2, 3, 4, 5 or 6.")
    except FileNotFoundError:
        print("File not found.")

if __name__ == "__main__":
    main()
