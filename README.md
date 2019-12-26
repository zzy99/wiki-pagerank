# wiki-pagerank
互联网数据挖掘第一次作业

——pagerank 计算



**数据处理**

 首先从 wikidump 下载 60+GB 的 xml 文件

 解析xml 的方法有很多，如 DOM、SAX、ElementTree 等，但是我这次采用了 ElementTree， 它与 DOM 相比速度更快，与 SAX 相比同样可以用 iterparse 函数，不会一次性在内存中 读入整个文档。这对于本次大文件读取是关键的。

 具体来说，本次利用 python 的 lxml 库，使用 etree 的 iterparse 方法，逐个读取文件中的 每个 element 并获取其标签。

 经过研究数据结构，发现对于本次计算有用的标签有下列几个：

<page>代表一个词条的整个页面

<title>是词条的名称

<id>是词条的序号（本次不采用，而是直接用 title 代表一个词条）

<text>是词条正文，我们要求的外链就在此中，并且处于双中括号[[]]中

 我们采用循环遍历每个 tag，每到一个page 处，就记录下 title，并从text 中用正则表达式 提取出外链，最后都存储下来，存储格式为字典{“title1”:[“外链 1”,”外链 2”,…], “title2”:[“外链

1”,”外链 2”,…],…}，其实就是我们熟悉的邻接表结构。

 

 

 

 

 

**算法描述**

 pagerank 算法其实很简单，在我们上一步能够得出转移矩阵P 后，直接用 PT 与 pagerank

值向量 π相乘，反复多次后就能收敛。（马尔科夫过程）

 

![img](file:///C:/Users/80431/AppData/Local/Temp/msohtmlclip1/01/clip_image002.jpg)

 

 我们这里主要处理这个矩阵向量乘法。直接在 python 中乘是不现实的：首先这个矩阵是

106*106 的，内存不够肯定不能直接运行；而且它也是稀疏的，之前已经用邻接表结构存 储，完全没有必要用这个大矩阵。

 于是我回想到之前学的并行与分布式计算，曾经提到了矩阵向量乘法不同的分解方法：

（按行、按列、按块）



 传统的按行分解

![img](file:///C:/Users/80431/AppData/Local/Temp/msohtmlclip1/01/clip_image003.jpg)

 



 按列分解

![img](file:///C:/Users/80431/AppData/Local/Temp/msohtmlclip1/01/clip_image005.jpg)

 

那我们这里显然可以采用第二种方式。矩阵的第一列，转置前就是第一行，这一行我们很 熟悉——它就是我们已经存在邻接表里的 x1 网页相应的出链，把他与x1 相乘，就能得到

x1 对所有页面的贡献，也就是乘后向量的第一列，然后x2、x3…都这样依次相加，就得到

了全部页面对全部页面的贡献，数学上也就是图中的按列相乘，列与列相加的最终结果。

 

 

 



 实际操作后发现，我们采样的数据量很小，存在排序泄露和排序沉入问题，导致收敛速 度很慢而且 pr 值不合理（迭代 20、50、100 次的结果相差很大，而且少数值过大，以及 大量的 0 值）。于是我加入了 RWR 的改进，在随机游走过程中重新浏览新网页，也就是 在原来的迭代中加入阻尼因数 α=0.85。事实证明这条改动是大有用处的。

 

![img](file:///C:/Users/80431/AppData/Local/Temp/msohtmlclip1/01/clip_image007.jpg)

**结果分析**

   收敛情况

分别设置迭代次数为 1、10、20、50，输出到文件中，观察数值变化及收敛情况。 下图依次是 1、10、20、50 次迭代后第一页的词条及结果，可以发现，10 次后已经趋

于稳定，而 50 次的结果已经和 20 次相差无几（pr 值小数点九位前都没有任何变化，100 万 个词条的排名也完全一样），至此已经可以得出收敛的结论。

![img](file:///C:/Users/80431/AppData/Local/Temp/msohtmlclip1/01/clip_image009.gif)

 

![img](file:///C:/Users/80431/AppData/Local/Temp/msohtmlclip1/01/clip_image011.jpg)![img](file:///C:/Users/80431/AppData/Local/Temp/msohtmlclip1/01/clip_image013.jpg)

 

 

   结果分布

通过 matplotlib 绘图，得到数据的分布图。可以发现，pr 值虽然从 1e-7 到 1e-3 都有， 但是主要还是集中在 1e-7~1e-6 之间，高于 1e-6 的仅有 23130 个词条，高于1e-5 的 仅有 589 条。

![img](file:///C:/Users/80431/AppData/Local/Temp/msohtmlclip1/01/clip_image015.jpg)

 

   热门词条

![img](file:///C:/Users/80431/AppData/Local/Temp/msohtmlclip1/01/clip_image018.gif)我选取了 100 万中排名前100 个词条，翻译成中文，可以看出美国人口普查相关内容 占很大的比重，而且其中人种中白人排第一。除此之外，英国是排名最高的国家，纽 约是排名最高的城市。当然，我们只在wiki 里选了100 万个词条，得到的这些信息也 只能代表前 100 万词条的趋势罢了。

 

 