import os
import mido

def change_bpm():
    # 获取用户输入的文件路径
    midi_file_path = input('Please enter MIDI file path: ')

    # 打开MIDI文件
    midi_file = mido.MidiFile(midi_file_path)

    # 获取原始 BPM 值
    original_tempo = 0
    original_bpm = 90
    for msg in midi_file:
        if msg.type == 'set_tempo':
            original_tempo = msg.tempo
            original_bpm = mido.tempo2bpm(original_tempo)
            break
    
    print( "original_tempo: {:.2f}".format(original_bpm))
    new_bpm = float(input('Please enter new BPM: '))

    # 更新 MIDI 文件的时间刻度和 BPM 值
    for track in midi_file.tracks:
        for msg in track:
            if hasattr(msg, 'time'):
                msg.time = int(msg.time * new_bpm / original_bpm)
            if msg.type == 'set_tempo':
                msg.tempo = mido.bpm2tempo(new_bpm)

    # 获取新文件名和路径
    file_name, file_ext = os.path.splitext(midi_file_path)
    new_file_path = file_name + '_new' + file_ext

    # 保存修改后的MIDI文件
    midi_file.save(new_file_path)

    return new_file_path

if __name__ == '__main__':
    # 更改BPM并输出新文件
    new_file_path = change_bpm()
    print(f'New file saved as {new_file_path}')
