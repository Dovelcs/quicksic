import os
import platform

# 获取当前文件路径
CurrentPath = os.path.dirname(os.path.abspath(__file__))

maxlist = 100

# 递归查找当前路径下所有.o文件
def search_file_o(path):
    file_list = []
    if platform.system() == "Windows":
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".o"):
                    file_list.append(os.path.join(root, file))
    if platform.system() == "Linux":
        # 使用find命令快速查找
        print("find O 文件")
        file_list = os.popen(f"find {path} -name '*.o'").readlines()
        # 去掉路径中的空白
    file_list = [i.strip() for i in file_list]
    return file_list


# 递归查找当前目录下所有的.c.h.cpp.s文件，并将内容保存为列表返回
def search_file_all(path):
    file_list = []
    if platform.system() == "Windows":
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".c") or file.endswith(".h") or file.endswith(".cpp") or file.endswith(".s"):
                    file_list.append(os.path.join(root, file))
    if platform.system() == "Linux":
        # 使用find命令快速查找
        print("查找 .C 源文件")
        file_list = os.popen(f"find {path} -name '*.c'").readlines()
        print("查找 .H 源文件")
        file_list += os.popen(f"find {path} -name '*.h'").readlines()
        print("查找 .cpp 源文件")
        file_list += os.popen(f"find {path} -name '*.cpp'").readlines()
        print("查找 .s 源文件")
        file_list += os.popen(f"find {path} -name '*.s'").readlines()

    # 去掉路径中的空白
    file_list = [i.strip() for i in file_list]
    return file_list


# 传入路径，以及文件列表。取出路径中的文件名并去掉后缀，
# 然后加上.s.c.cpp然后在文件列表中查找，如果存在对应的文件则返回对应的路径
def search_file(path, file_list):
    global source_list
    filename = os.path.basename(path)[:-2]
    # print(f"find c  filename {filename}")
    i = 0
    # 遍历文件列表，返回文件路径和列表下标
    for file in file_list:
        # print(f"find c {file}")
        if (filename + ".s" == os.path.basename(file) or
                filename + ".c" == os.path.basename(file)
                or filename + ".cpp" == os.path.basename(file)):
            del source_list[i]
            return file
        i += 1
    return None


# 传入一个c文件路径，一个文件列表。打开该c文件并找到所有的#include，然后找到对应的".h"文件，
# 判断文件列表中是否存在，如果存在则保存为列表，查找结束返回集合列表
def search_include(path, file_list):
    file_h = []
    global maxlist
    global source_list
    mlist = 0
    try :
        with open(path, "r", encoding="utf-8", errors='ignore') as f:
            lines = f.readlines()
            for line in lines:
                mlist +=1
                if mlist > maxlist:
                    break
                if "#include" in line and "<" not in line:
                    filename = line[line.find("\"") + 1:-2]
                    i = 0
                    for tmp in file_list:
                        if filename == os.path.basename(tmp):
                            # print(f"find h {filename}")
                            file_h.append(tmp)
                            del source_list[i]
                            break
                        i += 1
            file_h = list(set(file_h))
            return file_h
    except Exception as e:
        print(path)
        print(e)
        return file_h


# 实现进度条，不依赖三方库实现,精确到千分之一，要求不能换行刷新
def progress_bar(percent, width=50):
    if percent > 100:
        percent = 100
    # 计算进度条需要多少个#
    num = int(width * percent / 100)
    print("\r[{0}{1}] {2:.2f}%".format("#" * num, " " * (width - num), percent), end="")


if __name__ == '__main__':
    # CurrentPath = input("请输入工程路径：")
    c_file = []
    h_file = []
    print(CurrentPath)
    source_list = search_file_all(CurrentPath)
    mid_list = search_file_o(CurrentPath)
    print(f"一共查找到 {len(source_list)} 个源文件")
    #计算下标以显示进度条使用
    print("正在查找C文件，请稍等...")
    for percents, file in enumerate(mid_list):
        cfile = search_file(file, source_list)
        if file:
            c_file.append(cfile)
        progress_bar((percents / len(mid_list) * 100), width=50)
    progress_bar(100, width=50)
    c_file = list(filter(None,c_file))
    print("\n")
    print("正在查找H文件，请稍等...")

    for percents, file in enumerate(c_file):
        h = search_include(file, source_list)
        if h:
            h_file += h
        progress_bar((percents / len(c_file) * 100), width=50)
    progress_bar(100, width=50)
    print("\n")
    # 因为可能重复包含所以去掉重复的h文件
    h_file = list(set(h_file))
    h_file = list(filter(None,h_file))
    sourceinsight_filename = input("请输入sourceinsight文件名：")
    if sourceinsight_filename:
        sourceinsight_filename += ".txt"
        with open(os.path.join(CurrentPath, sourceinsight_filename), "w", encoding="utf-8") as f:
            for file in c_file:
                f.write(file + '\n')
            for file in h_file:
                f.write(file + '\n')
