from gossip import GossipNode

# 获取用户输入的端口
port = int(input("Enter the port for this node: "))

# 获取连接节点的端口，并转换为整数列表
connected_nodes_input = input("Enter the ports for the nodes connected to this node, separated by commas: ")

# 将输入的端口字符串转为整数列表
connected_nodes = [int(port) for port in connected_nodes_input.split(',')]

# 创建 GossipNode 实例
node = GossipNode(port, connected_nodes)
