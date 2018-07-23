# /usr/bin/python3
# -*- coding : utf-8 -*-
# 最大堆---完全二叉树，用list存储
# __author__ = mas


import time


class MaxHeap(object):
    def __init__(self, l, size, capacity):
        self.l = iter(l)
        self.size = size
        self.capacity = capacity

    def insertNode(self, tree, x):
        if tree:
            tree.append(x)
            x_loction = len(tree) - 1
            i = int(len(tree)/2) - 1
            while i >= 0 and x > tree[i]:
                tree[i], tree[x_loction] = tree[x_loction], tree[i]
                x_loction = i
                i = int((i + 1)/2) - 1

            return tree

        else:
            tree.append(x)

        return tree

    def initMaxHeap(self):
        l = self.l
        tree = []
        size = self.size
        capacity = self.capacity
        while True:
            try:
                if size < capacity:
                    x = next(l)
                    tree = self.insertNode(tree, x)
                    print('insert %d' % x, tree)
                    # self.preOrder(tree)
                    # print()
                    # self.midOrder(tree)
                    # print('\n############################')
                    size += 1
                else:
                    print('is full, need push a job, wait.')
                    time.sleep(1)
                    tree = self.delMaxNode(tree)
                    print('delete max', tree)
                    # self.preOrder(tree)
                    # print()
                    # self.midOrder(tree)
                    # print('\n############################')
                    size -= 1

            except Exception as e:
                print(e)
                print('all jobs is submit.')
                break

        while tree:
            tree = self.delMaxNode(tree)
            print('delete max', tree)
            # self.preOrder(tree)
            # print()
            # self.midOrder(tree)
            # print('\n############################')
            print('push job, wait.')
            time.sleep(1)

        print('all jobs as done.')

    def delMaxNode(self, tree):
        if tree:
            print('push %d' % tree[0])
            tree[0] = tree[-1]
            tree = tree[:-1]
            now_location = 0
            left = (now_location + 1) * 2 - 1
            right = (now_location + 1) * 2
            while left < len(tree) or right < len(tree):
                if right < len(tree):
                    '''
                    因为右儿子不超过，左儿子肯定不会超过
                    '''
                    if tree[left] > tree[right] and tree[left] > tree[now_location]:
                        tree[now_location], tree[left] = tree[left], tree[now_location]
                        now_location = left
                        left = (now_location + 1) * 2 - 1
                        right = (now_location + 1) * 2
                    elif tree[right] > tree[left] and tree[right] > tree[now_location]:
                        tree[now_location], tree[right] = tree[right], tree[now_location]
                        now_location = right
                        left = (now_location + 1) * 2 - 1
                        right = (now_location + 1) * 2

                    else:
                        return tree

                elif left < len(tree):
                    if tree[left] > tree[now_location]:
                        tree[now_location], tree[left] = tree[left], tree[now_location]
                        now_location = left
                        left = (now_location + 1) * 2 - 1
                    else:
                        return tree

        else:
            print('tree is empty.')

        return tree

    def searchNode(self, tree, x):
        pass

    # 还需要修改前中后序遍历
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

if __name__ == '__main__':
    MHTree = MaxHeap([46, 5, 4, 8, 6, 41, 53, 48, 1, 54, 3], 0, 5)
    tree = MHTree.initMaxHeap()

