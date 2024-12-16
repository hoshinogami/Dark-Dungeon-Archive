import threading
import tkinter as tk
import time
from archiving import find_archive_name, save_game, cover_game, auto_save_game
steam_archive_url=''
# 初始化定时器状态
timer_on = False
timer_thread = None
def timer_function(path):
    global steam_archive_url
    num=0
    while timer_on:
        print("定时器运行中...")
        if num%600==0:
            name=auto_save_game(steam_archive_url,path)
            listbox.insert(tk.END,name)
        num+=1
        time.sleep(1)  # 每秒执行一次

def on_submit():
    """手动读取存档路径"""
    user_input = entry.get()
    if user_input:
        print("用户输入:", user_input)
        # 你可以在这里添加更多逻辑，例如将输入添加到 Listbox 中
        # listbox.insert(tk.END, user_input)
        global steam_archive_url
        steam_archive_url=user_input
        items =find_archive_name(steam_archive_url)
        for item in items:
            listbox.insert(tk.END,item)

        entry.delete(0, tk.END)  # 清空输入框
    else:
        print("输入框为空！")


def on_button_click(label):
    """获取选中项按钮点击事件处理函数"""
    selected_indices = listbox.curselection()
    if selected_indices:
        selected_items = [listbox.get(i) for i in selected_indices]
        if label=='按钮1':
            global timer_on, timer_thread
            if timer_on:
                # 关闭定时器
                timer_on = False
                btn1.config(text="自动存档")  # 更新按钮文本
                if timer_thread is not None:
                    timer_thread.join()  # 等待线程结束
            else:
                # 开启定时器
                timer_on = True
                btn1.config(text="停止存档")  # 更新按钮文本
                timer_thread = threading.Thread(target=timer_function,args=(selected_items[0],))
                timer_thread.start()  # 启动线程
        elif label=='按钮2':
            path_name=save_game(steam_archive_url,selected_items[0])
            listbox.insert(tk.END, path_name)
        elif label== '按钮3':
             cover_game(steam_archive_url,selected_items[0])
             listbox.delete( selected_indices[0])
        # print(f"{label}: 选中的项目: {selected_items}")
    else:
        print(f"{label}: 没有选中任何项目！")


# 创建主窗口对象
root = tk.Tk()
root.title("暗黑地牢存档")
root.resizable(False, False)

root.geometry("800x700")
root.configure(bg='black')

# 设置窗口大小为800x700像素
root.geometry("800x700")

# 创建输入框和提交按钮，并放置在窗口顶部
entry_frame = tk.Frame(root, bg='#A9A9A9')  # 深灰色背景
entry_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=(20, 10))

entry = tk.Entry(entry_frame, font=("Arial", 12))
entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

submit_button = tk.Button(
    entry_frame,
    text="修改路径",
    command=on_submit,
    bg='#A9A9A9',  # 深灰色背景颜色
    fg='#FFD700',  # 暗黄色文本颜色
    font=("Arial", 12, "bold"),  # 字体
    borderwidth=0,  # 边框宽度
    activebackground='#A9A9A9',  # 激活时的背景颜色
    activeforeground='#FFD700'  # 激活时的文本颜色
)
submit_button.pack(side=tk.RIGHT)

# 创建 Listbox 并设置固定高度和宽度
listbox_frame = tk.Frame(root, bg='#A9A9A9', height=500)
listbox_frame.pack(pady=10, padx=20, fill=tk.X)

listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE, height=26, width=80, bg='#A9A9A9', fg='black', font=("Arial", 12),
                     selectbackground='#556B2F', selectforeground='#FFD700')  # 选中项的背景色和前景色
# 创建 Scrollbar 并关联到 Listbox
scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
listbox.config(yscrollcommand=scrollbar.set)

# 布局管理
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# 确保 listbox_frame 的高度保持为500px
listbox_frame.pack_propagate(False)

# 创建一个 Frame 来容纳三个按钮，并使它们并列一排
button_frame = tk.Frame(root, bg='black')
button_frame.pack(pady=20)

# 创建三个并列的按钮
buttons = [
    ("自动存档", "按钮1"),
    ("手动存档", "按钮2"),
    ("存档覆盖", "按钮3")
]
btn1=None

for label, button_label in buttons:
    btn = tk.Button(
        button_frame,
        text=label,
        command=lambda lbl=button_label: on_button_click(lbl),
        bg='#A9A9A9',  # 暗灰色背景颜色
        fg='#FFD700',  # 暗黄色文本颜色
        font=("Arial", 14, "bold"),  # 字体
        borderwidth=0,  # 边框宽度
        activebackground='#A9A9A9',  # 激活时的背景颜色
        activeforeground='#FFD700'  # 激活时的文本颜色
    )
    btn.pack(side=tk.LEFT, padx=10)

    if button_label=="按钮1":
        btn1=btn
# 运行主事件循环
root.mainloop()