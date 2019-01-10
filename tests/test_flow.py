# coding: utf-8
import pytest
from ething.core.utils.dataflow import Flow, Node, DebugNode


class StartNode(Node):

    OUTPUTS = ['default']

    def main(self):
        self.emit(2)


def test_flow():

    flow = Flow()

    node0 = StartNode(flow)
    node1 = DebugNode(flow)

    flow.connect(node0, node1)

    flow.run()

    assert flow.get_info(node0).get('count') == 1
    assert flow.get_info(node1).get('count') == 1



