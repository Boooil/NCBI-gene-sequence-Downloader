# ReadMe

本下载器对NCBI的核苷酸数据库内已知GenBank号的来自不同物种的同名称基因实现快速抓取，抓取文件将以“**物种名称\_GenBank号\_基因名称\_序列位置.fasta**”格式命名。

下载文件可用于不同物种间某基因核苷酸序列的比对与遗传进化树的绘制（需要借助其他程序进行）。

本代码成功建立一种大批量、自动化下载NCBI数据库中的指定基因（核苷酸）序列的方法，以减少不必要的重复性工作、提高遗传演化分析的效率。

## How to use

本下载器使用Python语言进行编写。

网页的自动化解析由selenium和lxml完成，资源下载由urllib完成。

需要配置selenium。

-   修改下载文件的保存路径

    将savepath\_prefix修改为自定义的文件夹路径。
    ```python
    savepath_prefix = 'file save path prefix'
    ```
-   修改导入Gebank表格的路径

    目前只支持csv格式。

    将csv\_path修改为自定义的文件路径。
    ```python
    csv_path = '*.csv'
    ```
    csv文件需要严格按照serum\_type,representative\_strain,GenBank三列标题进行内容填写，serum\_type是**血清类型**，representative\_strain是**代表株**，GenBank是**编号**，其中血清类型和GenBank**编号**是必填项，**代表株**是选填项。

执行downloader.py代码即可开始爬取和下载。
