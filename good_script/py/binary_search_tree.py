# !/usr/bin/python3
# -*- coding:utf-8 -*-
# search and insert binary tree
# __author__: mas

import sys


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


class SearchInsertTree(object):
    def __init__(self, data_list):
        self.data_list = iter(data_list)

    def compareTwoStr(self, str1, str2):
        '''
        find which str is larger, return 1 if str1 is larger, return 2 if 2 is larger, if equal return 0
        '''
        if len(str1) > len(str2):
            result = 1
            mlen = len(str2)
        elif len(str1) < len(str2):
            result = 2
            mlen = len(str1)
        else:
            result = 0
            mlen = len(str1)
        i = 0
        while i <= mlen - 1:
            if str1[i] > str2[i]:
                return 1
            elif str1[i] < str2[i]:
                return 2
            else:
                i += 1
                continue
        return result

    def insert_node(self, data):
        '''
        对现有的二叉树进行插值，左儿子 < 根节点 < 右儿子
        如果出现数据属性不同，则返回None
        属性相同则进行正确插值
        '''
        bt = self.bt
        if type(bt[0].node) != type(data):
            print('The type of data in list are not equal, please check your data.')
            self.bt = [BTNode(None)]
        else:
            if isinstance(bt[0].node, str):
                i = 0
                not_insert = True
                while not_insert:
                    # print('%s compare' % data, i, bt[i].node, self.compareTwoStr(data, bt[i].node), bt[i].lchild, bt[i].rchild)
                    if self.compareTwoStr(data, bt[i].node) == 1 and bt[i].rchild is not None:
                        i = bt[i].rchild
                    elif self.compareTwoStr(data, bt[i].node) == 1 and bt[i].rchild is None:
                        bt[i].set_rchild(len(bt))
                        bt.append(BTNode(data))
                        self.bt = bt
                        not_insert = False

                    elif self.compareTwoStr(data, bt[i].node) == 2 and bt[i].lchild is not None:
                        i = bt[i].lchild
                    elif self.compareTwoStr(data, bt[i].node) == 2 and bt[i].lchild is None:
                        # print('%s compare' % data, i, bt[i].node, self.compareTwoStr(data, bt[i].node), len(bt))
                        bt[i].set_lchild(len(bt))
                        bt.append(BTNode(data))
                        self.bt = bt
                        not_insert = False

                    else:
                        print('log : %s have been in bt.' % data)
                        self.bt = bt
                        not_insert = False

            else:
                i = 0
                not_insert = True
                while not_insert:
                    if data > bt[i].node and bt[i].rchild is not None:
                        i = bt[i].rchild
                    elif data > bt[i].node and bt[i].rchild is None:
                        bt[i].set_rchild(len(bt))
                        bt.append(BTNode(data))
                        self.bt = bt
                        not_insert = False

                    elif data < bt[i].node and bt[i].lchild is not None:
                        i = bt[i].lchild
                    elif data < bt[i].node and bt[i].lchild is None:
                        bt[i].set_lchild(len(bt))
                        bt.append(BTNode(data))
                        self.bt = bt
                        not_insert = False

                    else:
                        print('log : %d have been in bt.' % data)
                        self.bt = bt
                        not_insert = False

    def createBTTree(self):
        '''
        需要对data_list这迭代器进行遍历，加入到二叉搜索树中
        '''
        data_list = self.data_list
        bt = []
        try:
            next_data = next(data_list)
            have_data = True  # 判断是否有数据，没有数据下面就获取不出数据了
            bt.append(BTNode(next_data))
        except:
            bt.append(BTNode(None))
            have_data = False
        self.bt = bt

        while have_data and bt[0].node is not None:
            try:
                next_data = next(data_list)
                self.insert_node(next_data)
            except:
                have_data = False

        self.bt = bt


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


print()
MSTtree = SearchInsertTree(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'Auguest', 'September', 'October', 'November', 'December', 'July'])
MSTtree.createBTTree()
print('\n十二月英文二叉搜索树：')
print('先序：')
MSTtree.preOrderTrave(0)
print()
print('中序：')
MSTtree.midOrderTrave(0)
print()
print('后序：')
MSTtree.backOrderTrave(0)

print('\n\n####################################################\n')

NSTtree = SearchInsertTree([45, 64, 67, 4, 6, 81, 31, 81])
NSTtree.createBTTree()
print('\n数值二叉搜索树：')
print('先序：')
NSTtree.preOrderTrave(0)
print()
print('中序：')
NSTtree.midOrderTrave(0)
print()
print('后序：')
NSTtree.backOrderTrave(0)
print('\n')




