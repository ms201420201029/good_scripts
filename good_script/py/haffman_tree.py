# /usr/bin/python3
# -*- coding : utf-8 -*-
# 哈夫曼树(WPL最小)---haffman tree 根据搜索内容出现的频率来放置节点，使之达到搜索的复杂度最小
# 应用：可以根据哈夫曼树来调整各个判断的先后；可用于对某些字符进行编码，出现频率低的编码长一些
# __author__ = mas


class BTNode(object):
    def __init__(self):
        self.left = None
        self.right = None
        self.value = None


class haffmanTree(object):
    def __init__(self, l):
        self.l = l

    def initHaffmanTree(self):
        l = self.l
        l = sorted(l)
        tree_dict = {}

        while len(l) > 1:
            tree = BTNode()
            # two_node = l[:2]
            if l[0] not in tree_dict.keys() and l[1] not in tree_dict.keys():
                tree.left = l[0]
                tree.right = l[1]
                tree.value = l[0] + l[1]
            elif l[0] in tree_dict.keys():
                '''
                不会存在最小两个数都在tree_dict内
                '''
                tree.left = tree_dict[l[0]]
                tree_dict.pop(l[0])
                tree.right = l[1]
                tree.value = l[0] + l[1]
            elif l[1] in tree_dict.keys():
                tree.left = l[0]
                tree.right = tree_dict[l[1]]
                tree_dict.pop(l[1])
                tree.value = l[0] + l[1]

            l = l[2:]
            l.append(tree.value)
            l = sorted(l)

            tree_dict[tree.value] = tree

        return tree

    def preOrder(self, tree):
        if tree and not isinstance(tree, int):
            print(tree.value, end=" ")
            self.preOrder(tree.left)
            self.preOrder(tree.right)
        elif isinstance(tree, int):
            print(tree, end=" ")

    def midOrder(self, tree):
        if tree and not isinstance(tree, int):
            self.midOrder(tree.left)
            print(tree.value, end=" ")
            self.midOrder(tree.right)
        elif isinstance(tree, int):
            print(tree, end=" ")

    def backOrder(self, tree):
        if tree and not isinstance(tree, int):
            self.backOrder(tree.left)
            self.backOrder(tree.right)
            print(tree.value, end=" ")
        elif isinstance(tree, int):
            print(tree, end=" ")

if __name__ == '__main__':
    HFMTree = haffmanTree([1, 2, 3]) # ([3, 4, 2, 3, 5, 1, 6, 3, 8, 4, 34])
    tree = HFMTree.initHaffmanTree()
    print('pre order:')
    HFMTree.preOrder(tree)
    print('\nmid order:')
    HFMTree.midOrder(tree)
    print('\nback order:')
    HFMTree.backOrder(tree)
    print()





















