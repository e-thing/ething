# coding: utf-8
import objectpath


def generate_ressource_filter(expr):
    def _filter(r):
        try:
            tree = objectpath.Tree(r.toJson())
            return bool(tree.execute(expr))
        except:
            return False
    return _filter