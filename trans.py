import re
import html
from urllib import parse
import requests
import time
import os

GOOGLE_TRANSLATE_URL = 'http://translate.google.com/m?q=%s&tl=%s&sl=%s'

def translate(text, to_language="auto", text_language="auto"):

    ptext = parse.quote(text)
    url = GOOGLE_TRANSLATE_URL % (ptext,to_language,text_language)
    response = requests.get(url)
    time.sleep(0.2)
    data = response.text
    expr = r'(?s)class="(?:t0|result-container)">(.*?)<'
    result = re.findall(expr, data)
    if (len(result) == 0):
        return ""
    print(text + ' → ' + result[0])
    return html.unescape(result[0])

def get_trans():
    scenes_dir = 'scenes'
    for scene_folder in os.listdir(scenes_dir):
    
        scene_id = scene_folder[1:7]
        
        if "_" in scene_folder:
            form = 2
        else:
            form = 1
            
        # 检查是否包含spines文件夹
        folder_path = os.path.join(scenes_dir, scene_folder)
        is_spines = os.path.exists(os.path.join(folder_path, 'spines'))
        
        preprocess(folder_path)        
        script_conversion_cn(folder_path, folder_path + "/script_pre.txt", is_spines)


def script_conversion_cn(folder_path, script_pre, is_spine):

    if os.path.exists(folder_path+'/script_cn.txt'):
        print(folder_path+'/script.txt_cn'+"已存在!")
        return

    voice_num = 0
    # 打开原始文件
    with open(script_pre, 'r', encoding='utf-8') as f:
        # 读取所有行
        lines = f.readlines()
        # 创建一个空列表，用于存储转换后的行
        new_lines = []
        # 在列表中添加第一行固定内容
        new_lines.append('<BGM_PLAY>fkg_bgm_hscene001,1000\n')
        n_line = 1
        n_lines = len(lines)
        # 遍历原始文件的每一行
        for line in lines:
            print( str(n_line) + '/'+ str(n_lines))
            if line == '':
                continue
            # 去掉行尾的换行符
            line = line.strip()
            # 去掉可能存在的 BOM 字符
            line = line.replace('\ufeff', '')
            # 如果行以 mess 开头，表示是对话内容
            if line.startswith('mess,'):
                # 用逗号分割行，得到四个部分
                parts = line.split(',')
                # 如果第二个部分为空，表示是内心对白
                if parts[1] == '':
                    # 在列表中添加<NAME_PLATE>标签和对白内容
                    new_lines.append('<NAME_PLATE>\n')
                    new_lines.append(parts[2] + ' \\n' + translate(parts[2], "zh-CN","ja") + '\n')
                    # 在列表中添加<PAUSE>标签
                    new_lines.append('<PAUSE>\n')
                # 如果第二个部分不为空，表示是人物对白
                else:
                    # 如果第四个部分不为空，表示有音频名称
                    if parts[3] != '':
                        voice_num += 1
                        # 在列表中添加<VOICE_PLAY>标签和音频名称，其中音频名称需要去掉 ID，只保留 fkg_ 开头的部分
                        new_lines.append('<VOICE_PLAY>' + parts[3].split('/')[1] + '\n')
                    # 在列表中添加<NAME_PLATE>标签和人物名字
                    new_lines.append('<NAME_PLATE>' + parts[1] + ' ' + translate(parts[1], "zh-CN","ja") + '\n')
                    # 在列表中添加对白内容
                    new_lines.append(parts[2] + ' \\n' + translate(parts[2], "zh-CN","ja") + '\n')
                    # 在列表中添加<PAUSE>标签
                    new_lines.append('<PAUSE>\n')
            # 如果行以 effect 开头，表示是特效内容
            elif line.startswith('effect'):
                # 用逗号分割行，得到四个部分
                parts = line.split(',')
                # 如果第二个部分是 3，表示是白色淡入效果
                if parts[1] == '3':
                    # 在列表中添加<FADE_IN>标签和参数
                    new_lines.append('<FADE_IN>white,670\n')
                # 如果第二个部分是 4，表示是闪烁效果的结束
                elif parts[1] == '4':
                    # 在列表中添加闪烁效果的最后一个标签和参数
                    new_lines.append('<FADE_OUT>white,670\n')
                    # 如果第二个部分是 5，表示是闪烁效果的开始
                elif parts[1] == '5':
                    # 在列表中添加闪烁效果的一系列标签和参数
                    new_lines.append('<FADE_OUT>white,100\n')
                    new_lines.append('<FADE_IN>white,100\n')
                    new_lines.append('<WAIT>100\n')
                    new_lines.append('<FADE_OUT>white,200\n')
                    new_lines.append('<FADE_IN>white,200\n')
                    new_lines.append('<WAIT>100\n')
                    new_lines.append('<FADE_OUT>white,200\n')
                    new_lines.append('<FADE_IN>white,200\n')
                # 如果第二个部分是 6，表示是淡出效果
                if parts[1] == '6':
                    # 在列表中添加<FADE_OUT>标签和参数
                    new_lines.append('<FADE_OUT>black,670\n')
                # 如果第二个部分是 7，表示是淡入效果
                elif parts[1] == '7':
                    # 在列表中添加<FADE_IN>标签和参数
                    new_lines.append('<FADE_IN>black,670\n')
            # 如果行以 image 开头，表示是图片内容
            elif line.startswith('image,'):
                # 用逗号分割行，得到四个部分
                parts = line.split(',')
                # 在列表中添加<EV>标签和参数，其中图片名称需要去掉前缀 hscene_r18/
                new_lines.append('<EV>' + parts[1].replace('hscene_r18/', '') + ',NONE,0\n')
            # 如果行以 message_window 开头，表示是界面显示内容
            elif line.startswith('message_window,'):
                # 用逗号分割行，得到三个部分
                parts = line.split(',')
                # 如果第二个部分是 0，表示是隐藏界面
                if parts[1] == '0':
                    # 在列表中添加<UI_DISP>标签和参数
                    new_lines.append('<UI_DISP>OFF,0\n')
                # 如果第二个部分是 1，表示是显示界面
                elif parts[1] == '1':
                    # 在列表中添加<UI_DISP>标签和参数
                    new_lines.append('<UI_DISP>ON,0\n')
            # 如果行以 spine 开头，表示是动画内容
            elif line.startswith('spine,'):
                is_spine = True
                # 用逗号分割行，得到六个部分
                parts = line.split(',')
                # 在列表中添加<SPINE>标签和参数，其中动画名称需要去掉前缀 hscene_r18_spine/
                new_lines.append(
                    '<SPINE>' + parts[1].replace('hscene_r18_spine/', '') + ',' + ','.join(parts[2:]) + '\n')
            # 如果行以 spine_play 开头，表示是动画播放内容
            elif line.startswith('spine_play,'):
                # 用逗号分割行，得到四个部分
                parts = line.split(',')
                # 在列表中添加<SPINE_PLAY>标签和参数，去掉最后的逗号
                new_lines.append('<SPINE_PLAY>' + ','.join(parts[1:-1]) + '\n')
            # 如果行以 spine_effect 开头，表示是动画特效内容
            elif line.startswith('spine_effect,'):
                # 用逗号分割行，得到四个部分
                parts = line.split(',')
                # 只有当第三个部分为空时，才会执行对特效的处理
                if parts[2] == '':
                    # 如果第二个部分是 3，表示是白色淡入效果
                    if parts[1] == '3':
                        # 在列表中添加<FADE_IN2>标签和参数
                        new_lines.append('<FADE_IN2>white,670\n')
                    # 如果第二个部分是 4，表示是闪烁效果的结束
                    elif parts[1] == '4':
                        # 在列表中添加闪烁效果的最后一个标签和参数
                        new_lines.append('<FADE_OUT2>white,670\n')
                    # 如果第二个部分是 5，表示是闪烁效果的开始
                    elif parts[1] == '5':
                        # 在列表中添加闪烁效果的一系列标签和参数
                        new_lines.append('<FADE_OUT2>white,100\n')
                        new_lines.append('<FADE_IN2>white,100\n')
                        new_lines.append('<WAIT2>100\n')
                        new_lines.append('<FADE_OUT2>white,200\n')
                        new_lines.append('<FADE_IN2>white,200\n')
                        new_lines.append('<WAIT2>100\n')
                        new_lines.append('<FADE_OUT2>white,200\n')
                        new_lines.append('<FADE_IN2>white,200\n')
                    # 如果第二个部分是 6，表示是黑色淡出效果
                    elif parts[1] == '6':
                        # 在列表中添加<FADE_OUT2>标签和参数
                        new_lines.append('<FADE_OUT2>black,670\n')
                # 如果第二个部分是 7，表示是黑色淡入效果
                if parts[1] == '7':
                    # 在列表中添加<FADE_IN2>标签和参数
                    new_lines.append('<FADE_IN2>black,670\n')
            # 如果行以 spine_wait 开头，表示是动画等待内容
            elif line.startswith('spine_wait,'):
                # 用逗号分割行，得到三个部分
                parts = line.split(',')
                # 在列表中添加<WAIT2>标签和参数，其中等待时间需要乘以 1000 转换为毫秒
                new_lines.append('<WAIT2>' + str(int(float(parts[1]) * 1000)) + '\n')
            n_line = n_line + 1
        # 在列表末尾添加固定内容
        new_lines.append('<BGM_STOP>500\n')
        new_lines.append('<UI_DISP>OFF, 500\n')
        new_lines.append('<BG_OUT>500\n')
        new_lines.append('<SCENARIO_END>')
    # 打开新的文件，用于写入转换后的内容
    with open(folder_path+'/script_cn.txt', 'w', encoding='utf-8') as f:
        # 遍历转换后的每一行
        for line in new_lines:
            # 写入文件，并在每一行后面加上换行符
            f.write(line)
    return is_spine,voice_num

def preprocess(path):
    with open(path + "/script_original.txt", 'r', encoding = 'utf-8') as f:
        text = f.read()
        text = text.replace('\\n', '。 ')
    with open(path + "/script_pre.txt", 'w', encoding = 'utf-8') as f:
        f.write(text)

get_trans()
print(translate("你吃饭了么？", "ja","zh-CN")) #汉语转日语
