# !/usr/bin/python3
# -*- coding:utf-8 -*-
# binary tree
# __author__: mas


class BTNode(object):
    def __init__(self, data):
        self.node = data
        self.lchild = None
        self.rchild = None

    def get_node(self):
        return self.node

    def set_lchild(self, l):
        self.lchild = l

    def get_lchild(self):
        return self.lchild

    def set_rchild(self, r):
        self.rchild = r

    def get_rchild(self):
        return self.rchild


class BTTree(object):
    def __init__(self, data_list):
        self.data_list = iter(data_list)

    def createBTTree(self):
        data_list = self.data_list
        bt = []
        try:
            next_data = next(data_list)
            i = 1
            have_data = True
        except:
            self.node = BTNode(None)
            have_data = False

        while have_data:
            if i == 1:
                print('append %s' % next_data)
                bt.append(BTNode(next_data))
                print(bt[i-1].node, bt[i-1].lchild, bt[i-1].rchild)
            else:
                bt.append(BTNode(next_data))
                fu = int(i/2)-1
                if i%2 == 0:
                    print('append %s' % next_data, i, fu)
                    bt[fu].set_lchild(i-1)
                else:
                    print('append %s' % next_data, i, fu)
                    bt[fu].set_rchild(i-1)
            try:
                next_data = next(data_list)
                i += 1
            except:
                have_data = False
        self.bt = bt

        print('cteate binary tree done.')

    def preOrderTrave(self, bt_number):
        if self.bt[bt_number] is not None:
            print(self.bt[bt_number].node, end=' ')
            if self.bt[bt_number].lchild is not None:
                self.preOrderTrave(self.bt[bt_number].lchild)
            if self.bt[bt_number].rchild is not None:
                self.preOrderTrave(self.bt[bt_number].rchild)

    def midOrderTrave(self, bt_number):
        if self.bt[bt_number] is not None:
            if self.bt[bt_number].lchild is not None:
                self.midOrderTrave(self.bt[bt_number].lchild)
            print(self.bt[bt_number].node, end=' ')
            if self.bt[bt_number].rchild is not None:
                self.midOrderTrave(self.bt[bt_number].rchild)

    def backOrderTrave(self, bt_number):
        if self.bt[bt_number] is not None:
            if self.bt[bt_number].lchild is not None:
                self.backOrderTrave(self.bt[bt_number].lchild)
            if self.bt[bt_number].rchild is not None:
                self.backOrderTrave(self.bt[bt_number].rchild)
            print(self.bt[bt_number].node, end=' ')

# bt = BTNode(3)
# print(bt.node, bt.lchild, bt.rchild)
# bt.set_lchild(4)
# bt.set_rchild(5)
# print(bt.node, bt.lchild, bt.rchild)
btree = BTTree(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'])
btree.createBTTree()
btree.preOrderTrave(0)
print()
btree.midOrderTrave(0)
print()
btree.backOrderTrave(0)
print()

