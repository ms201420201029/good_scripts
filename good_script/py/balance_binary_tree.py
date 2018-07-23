# /usr/bin/python3
# -*- coding : utf-8 -*-
# 平衡二叉树：也叫AVL树，左右两个子树的高度绝对值不超过1，并且左右两棵子树也都是平衡二叉树，需要完成：建树、新增节点、查找、删除（基于字符串和数值）
# __author__ = mas

import math
import pandas as pd


class BTNode(object):
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.left_h = 0
        self.right_h = 0


class AVLTree(object):
    '''
    平衡二叉树，左右两个子树的高度绝对值不超过1
    '''
    def __init__(self, l):
        '''
        给定一个list，将其转化成为跌迭代器
        '''
        self.l = iter(l)

    def LLrotate(self, tree):
        new_tree = tree.left
        tree.left = new_tree.right
        new_tree.right = tree

        # 更新树高
        if new_tree.right.left:
            new_tree.right.left_h = max(new_tree.right.left.left_h, new_tree.right.left.right_h) + 1
        else:
            new_tree.right.left_h = 0
        new_tree.right.left_h = tree.left_h
        new_tree.right_h = max(new_tree.left_h, new_tree.right_h) + 1
        return new_tree

    def LRrotate(self, tree):
        if tree.left.right.left:
            new_tree = tree.left.right
            tree.left.right = new_tree.left
            new_tree.left = tree.left
            tree.left = None
            new_tree.right = tree

        elif tree.left.right.right:
            new_tree = tree.left.right
            tree.left.right = None
            new_tree.left = tree.left
            tree.left = new_tree.right
            new_tree.right = tree

        else:
            new_tree = tree.left.right
            tree.left.right = None
            new_tree.left = tree.left
            tree.left = None
            new_tree.right = tree

        # 更新树高
        if new_tree.left.right:
            new_tree.left.right_h = max(new_tree.left.right.left_h, new_tree.left.right.right_h) + 1
        else:
            new_tree.left.right_h = 0
        if new_tree.right.left:
            new_tree.right.left_h = max(new_tree.right.left.left_h, new_tree.right.left.right_h) + 1
        else:
            new_tree.right.left_h = 0
        new_tree.left_h = max(new_tree.left.left_h, new_tree.left.right_h) + 1
        new_tree.right_h = max(new_tree.right.left_h, new_tree.right.right_h) + 1

        return new_tree

    def RLrotate(self, tree):
        print(tree.right.left)
        if tree.right.left.left:
            new_tree = tree.right.left
            tree.right.left = None
            new_tree.right = tree.right
            tree.right = new_tree.left
            new_tree.left = tree

        elif tree.right.left.right:
            new_tree = tree.right.left
            tree.right.left = new_tree.right
            new_tree.right = tree.right
            tree.right = None
            new_tree.left = tree

        else:
            new_tree = tree.right.left
            tree.right.left = None
            new_tree.right = tree.right
            tree.right = None
            new_tree.left = tree

        # 更新树高
        if new_tree.left.right:
            new_tree.left.right_h = max(new_tree.left.right.left_h, new_tree.left.right.right_h) + 1
        else:
            new_tree.left.right_h = 0
        if new_tree.right.left:
            new_tree.right.left_h = max(new_tree.right.left.left_h, new_tree.right.left.right_h) + 1
        else:
            new_tree.right.left_h = 0
        new_tree.left_h = max(new_tree.left.left_h, new_tree.left.right_h) + 1
        new_tree.right_h = max(new_tree.right.left_h, new_tree.right.right_h) + 1

        return new_tree

    def RRrotate(self, tree):
        new_tree = tree.right
        tree.right = new_tree.left
        new_tree.left = tree

        # 更新树高
        if new_tree.left.right:
            new_tree.left.right_h = max(new_tree.left.right.left_h, new_tree.left.right.right_h) + 1
        else:
            new_tree.left.right_h = 0
        new_tree.left_h = max(new_tree.left_h, new_tree.right_h) + 1
        return new_tree

    def insertNode(self, tree, x):
        if tree:
            if x < tree.value:
                '''
                插在左子树上
                '''
                tree.left = self.insertNode(tree.left, x)

                if tree.left:
                    print('change {0} left height.'.format(tree.value))
                    tree.left_h = max(tree.left.left_h, tree.left.right_h) + 1
                    print('{0} left height is {1}'.format(tree.value, tree.left_h))
                if tree.right:
                    print('change {0} right height.'.format(tree.value))
                    tree.right_h = max(tree.right.left_h, tree.right.right_h) + 1
                    print('{0} right height is {1}'.format(tree.value, tree.right_h))

                if tree.left_h - tree.right_h == 2:
                    '''
                    需要左旋，因为插进一个数导致树不平衡，
                    因此，只能存在x大于或者小于下个节点的值
                    '''
                    if x < tree.left.value:
                        print('LL')
                        tree = self.LLrotate(tree)
                    else:
                        print('LR')
                        tree = self.LRrotate(tree)

            elif x > tree.value:
                '''
                插在右子树上
                '''
                tree.right = self.insertNode(tree.right, x)

                # 插入数据后需要对更新树高
                if tree.left:
                    print('change {0} left height.'.format(tree.value))
                    tree.left_h = max(tree.left.left_h, tree.left.right_h) + 1
                    print('{0} left height is {1}'.format(tree.value, tree.left_h))
                if tree.right:
                    print('change {0} right height.'.format(tree.value))
                    tree.right_h = max(tree.right.left_h, tree.right.right_h) + 1
                    print('{0} right height is {1}'.format(tree.value, tree.right_h))

                if tree.right_h - tree.left_h == 2:
                    '''
                    需要右旋
                    '''
                    if x < tree.right.value:
                        print('RL')
                        tree = self.RLrotate(tree)
                    else:
                        print('RR')
                        tree = self.RRrotate(tree)

            else:
                return tree

        else:
            tree = BTNode(x)

        # 经过旋转后，旋转的子树的高度是没问题的，但是其他树节点还需要更新高度
        if tree.left:
            print('change {0} left height.'.format(tree.value))
            tree.left_h = max(tree.left.left_h, tree.left.right_h) + 1
            print('{0} left height is {1}'.format(tree.value, tree.left_h))
        if tree.right:
            print('change {0} right height.'.format(tree.value))
            tree.right_h = max(tree.right.left_h, tree.right.right_h) + 1
            print('{0} right height is {1}'.format(tree.value, tree.right_h))

        return tree

    def initTree(self):
        tree = None
        l = self.l
        while True:
            # x = next(l)
            # print('insert {0}'.format(x))
            # tree = self.insertNode(tree, x)
            try:
                x = next(l)
                print('insert {0}'.format(x))
                tree = self.insertNode(tree, x)
                # self.preOrder(tree)
                # print()
                # self.midOrder(tree)
                # print('\n')
            except Exception as e:
                print(e)
                print('init tree is done.')
                return tree

    def delRotate(self, tree):
        if tree.left_h - tree.right_h == 2:
            '''
            需要左旋，因为左边子树比较高
            '''
            if  tree.left.left_h >= tree.left.right_h:
                '''
                左边高就相当于左边插了一个数
                等于的情况可以用左边插入一个数处理
                '''
                print('LL')
                tree = self.LLrotate(tree)
            elif tree.left.left_h < tree.left.right_h:
                print('LR')
                tree = self.LRrotate(tree)

        if tree.right_h - tree.left_h == 2:
            '''
            需要右旋
            '''
            if  tree.right.left_h > tree.right.right_h:
                print('RL')
                tree = self.RLrotate(tree)
            elif tree.right.left_h <= tree.right.right_h:
                print('RR')
                tree = self.RRrotate(tree)

        return tree

    def delNode(self, tree, x):
        '''
        删除并更新树高，如果平衡因子差距为2则旋转变成平衡树
        '''
        if tree and x:
            if x > tree.value:
                tree.right = self.delNode(tree.right, x)

                # 删除节点后，更新树高
                if tree.left:
                    tree.left_h = max(tree.left.left_h, tree.left.right_h) + 1
                else:
                    tree.left_h = 0
                if tree.right:
                    tree.right_h = max(tree.right.left_h, tree.right.right_h) + 1
                else:
                    tree.right_h = 0

                # 若需要旋转
                if tree.left_h - tree.right_h == 2 or tree.right_h - tree.left_h == 2:
                    tree = self.delRotate(tree)

            elif x < tree.value:
                tree.left = self.delNode(tree.left, x)

                # 删除节点后，更新树高
                if tree.left:
                    tree.left_h = max(tree.left.left_h, tree.left.right_h) + 1
                else:
                    tree.left_h = 0
                if tree.right:
                    tree.right_h = max(tree.right.left_h, tree.right.right_h) + 1
                else:
                    tree.right_h = 0

                # 若需要旋转
                if tree.left_h - tree.right_h == 2 or tree.right_h - tree.left_h == 2:
                    tree = self.delRotate(tree)

            elif tree.left and tree.right:
                temp = findMin(tree.right)
                tree.value = temp
                tree.right = self.delNode(tree.right, x)

                # 删除节点后，更新树高
                if tree.left:
                    tree.left_h = max(tree.left.left_h, tree.left.right_h) + 1
                else:
                    tree.left_h = 0
                if tree.right:
                    tree.right_h = max(tree.right.left_h, tree.right.right_h) + 1
                else:
                    tree.right_h = 0

                # 若需要旋转
                if tree.left_h - tree.right_h == 2 or tree.right_h - tree.left_h == 2:
                    tree = self.delRotate(tree)

            else:
                if tree.left:
                    tree = tree.left
                elif tree.right:
                    tree = tree.right
                else:
                    tree = None

                if tree:
                    # 删除节点后，更新树高
                    if tree.left:
                        tree.left_h = max(tree.left.left_h, tree.left.right_h) + 1
                    if tree.right:
                        tree.right_h = max(tree.right.left_h, tree.right.right_h) + 1

                    # 若需要旋转
                    if tree.left_h - tree.right_h == 2 or tree.right_h - tree.left_h == 2:
                        tree = self.delRotate(tree)

            if tree:
                # 经过旋转后，旋转的子树的高度是没问题的，但是其他树节点还需要更新高度
                if tree.left:
                    print('change {0} left height.'.format(tree.value))
                    tree.left_h = max(tree.left.left_h, tree.left.right_h) + 1
                    print('{0} left height is {1}'.format(tree.value, tree.left_h))
                if tree.right:
                    print('change {0} right height.'.format(tree.value))
                    tree.right_h = max(tree.right.left_h, tree.right.right_h) + 1
                    print('{0} right height is {1}'.format(tree.value, tree.right_h))

        return tree

    def searchNode(self, tree, x):
        if tree and data:
            if data > tree.value:
                return self.searchNode(tree.right, data)
            elif data < tree.value:
                return self.searchNode(tree.left, data)
            return 1

    def preOrder(self, tree):
        if tree:
            print(tree.value, end=" ")
            self.preOrder(tree.left)
            self.preOrder(tree.right)

    def midOrder(self, tree):
        if tree:
            self.midOrder(tree.left)
            print(tree.value, end=" ")
            self.midOrder(tree.right)

    def backOrder(self, tree):
        if tree:
            self.backOrder(tree.left)
            self.backOrder(tree.right)
            print(tree.value, end=" ")

    def findLongest(self, tree, max_len=0):
        if tree:
            if len(str(tree.value)) > max_len:
                max_len = len(str(tree.value))
            max_len = self.findLongest(tree.left, max_len)
            max_len = self.findLongest(tree.right, max_len)
        return max_len

    def visualTree(self, tree):
        '''
        当树层数很多时，树比较大，构建有些困难（此部分未完成）
        '''
        max_len = self.findLongest(tree)

        if max_len and max(tree.left_h, tree.right_h) > 0:
            limb = math.ceil(maxmax_len/2) + 1
            '''
            生成tree_value的list，这样有助于绘制图形（后续可以根据list填充dataframe，转置之后可以将树形状横过来---此处不实现）
            '''
            tree_list = [{'tree':[tree], 'value':[tree.value]}]
            for i in range(max(tree.left_h, tree.right_h)):
                dict = {'tree':[], 'value':[]}
                for t in tree_list[i]['tree']:
                    if t is None:
                        dict['tree'] = dict['tree'] + [None, None]
                        dict['value'] = dict['value'] + [None, None]
                    elif t.left and t.right:
                        dict['tree'] = dict['tree'] + [t.left, t.right]
                        dict['value'] = dict['value'] + [t.left.value, t.right.value]
                    elif t.left:
                        dict['tree'] = dict['tree'] + [t.left, None]
                        dict['value'] = dict['value'] + [t.left.value, None]
                    elif t.right:
                        dict['tree'] = dict['tree'] + [None, t.right]
                        dict['value'] = dict['value'] + [None, t.right.value]
                    else:
                        dict['tree'] = dict['tree'] + [None, None]
                        dict['value'] = dict['value'] + [None, None]
                tree_list.append(dict)

            tree_dataframe = pd.DataFrame(index=range(max(tree.left_h, tree.right_h) * 6 + 1), columns=range(2**len(tree_list) * limb))

            tree_len = len(tree_list)
            for i, d in enumerate(tree_list):
                value = d['value']
                for v in value:
                    print(2**(tree_list - i - 1))


if __name__ == '__main__':
    # AVLtree = AVLTree([1, 2, 3])
    # AVLtree = AVLTree(list(reversed([1, 2, 3, 4, 5, 6, 5, 7, 8, 9, 10, 8])))
    # tree = AVLtree.initTree()
    # print(tree.left_h, tree.right_h, tree.left.left_h, tree.left.right_h)
    # AVLtree = AVLTree(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'Auguest', 'September', 'October', 'November', 'December'])
    # tree = AVLtree.initTree()

    AVLtree = AVLTree([8, 7, 11, 6, 12, 10, 13, 9])
    tree = AVLtree.initTree()
    tree = AVLtree.delNode(tree, 6)
    print('pre order:')
    AVLtree.preOrder(tree)
    print('\nmid order:')
    AVLtree.midOrder(tree)
    print('\nback order:')
    AVLtree.backOrder(tree)
    print()

    # AVLtree.visualTree(tree)

