# coding: utf-8
from ething.core.flow.dataflow import Flow, Node


class StartNode(Node):

    OUTPUTS = ['default']

    def main(self):
        self.emit(2)

class EndNode(Node):

    INPUTS = ['default']

    def main(self, default):
        pass


def test_flow():

    flow = Flow()

    node0 = StartNode(flow)
    node1 = EndNode(flow)

    flow.connect(node0, node1)

    flow.run()

    assert flow.get_info(node0).get('count') == 1
    assert flow.get_info(node1).get('count') == 1


