---
title: hyperledger: 1.12.0 数据的不可变性
date: 2017-12-22 20:06:00
categories: blockchain/hyperledger
tags: [blockchain,hyperledger]
---

### 1. 区块链数据的不可变性
位于区块链上的数据的不变性可能是为当前记录在中央服务器上的各种社会经济过程部署基于区块链的解决方案最有力和最有说服力的理由。 这种不变性或“不会随时间变化而变化”使得区块链对于会计、金融交易、身份管理以及资产所有权、管理和转移有用，这只是一部分例子。 一旦交易被写入区块链，没有人可以改变它，或者至少，改变它是非常困难的。

根据R3研究总监安东尼·刘易斯（Antony Lewis）的说法，

“当人们说区块链是不可变的，并不意味着数据不能改变的时候，这意味着在没有合谋的情况下改变是非常困难的，而且如果你尝试了，那么检测这个尝试是非常容易的。”

让我们在这个说法上再深入一点。 要更改区块链中的交易是非常困难的，因为每个区块都通过包含前一个区块的hash链接到前一个区块。 这个hash包括前一个块中所有事务的Merkle根hash。 如果单个事务发生变化，不仅Merkle根hash将发生变化，而且变化块中包含的hash也会发生变化。 此外，每个后续块都需要更新以反映这一变化。 在工作量证明的情况下，重新计算该块和随后每个块的随机数所需的能量将是过高的。 另一方面，如果有人在一个块中修改了一个事务，而没有经过必要的步骤来更新后面的块，那么很容易重新计算块中使用的散列并确定有什么错误。

让我们来看一个这如何工作的例子。 在下面的图中，我们看到块11的原始块和事务。具体来说，我们看到块11中的事务的Merkle根是散列#ABCD，它是该块中四个事务的组合散列。 现在，假设有人进来并尝试将交易A更改为交易A'。 这反过来又修改了存储在Merkle树中的哈希，而Merkle根变成了哈希＃A'BCD。 另外，还需要修改存储在块12中的先前块散列以反映块11的散列的整体变化。

![](/static/images/docs/blockchain/hyperledger/BLOCKCHAIN_IMMUTABILITY.png)