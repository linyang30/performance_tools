import subprocess
import re
import time
import csv


def get_current_time():
    ct = time.strftime("%H:%M:%S", time.localtime())
    print('time:', ct)
    return ct


def get_phone_cpu_info():
    command = 'adb shell dumpsys cpuinfo'
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    out = str(p.stdout.readlines())
    result = str(re.findall(r'(\d+\.?\d?)% TOTAL: .', out)[0]) + '%'
    print('cpu:', result)
    return result

def get_phone_cpu_info2():
    command = 'adb shell top -n 1'
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    out = str(p.stdout.readlines())
    result = re.findall(r'(\d+)%cpu\s+\d+%user\s+\d+%nice\s+\d+%sys (\d+)%idle', out)[0]
    total = int(result[0])
    idle = int(result[1])
    res = str(round((total - idle) / total * 100)) + '%'
    print('cpu:', res)
    return res

def get_phone_cpu_info3():
    command = 'adb shell cat /proc/stat'
    totalCPUTime1 = 0
    totalCPUTime2 = 0
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    time.sleep(0.1)
    p2 = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    out = p.stdout.readline()

    res1 = out.decode('utf-8').split()[1:]
    idle1 = int(res1[3])
    for data in res1:
        totalCPUTime1 = totalCPUTime1 + int(data)

    out2 = p2.stdout.readline()
    res2 = out2.decode('utf-8').split()[1:]
    idle2 = int(res2[3])
    for data in res2:
        totalCPUTime2 = totalCPUTime2 + int(data)

    result = str(round(((totalCPUTime2 - idle2) - (totalCPUTime1 - idle1)) / (totalCPUTime2 - totalCPUTime1) * 100)) + '%'
    print('cpu:', result)
    return result


def get_phone_memory_info():
    command = 'adb shell cat /proc/meminfo'
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    out = str(p.stdout.readlines())
    total = int(re.findall(r'MemTotal:\s+(\d+) kB', out)[0])
    free = int(re.findall(r'MemAvailable:\s+(\d+) kB', out)[0])
    used = total - free
    result = str(round(used / total * 100)) + '%'
    print('memory:', result)
    return result


def get_cpu_freg(cpu_core_number):
    commandList = []
    cpuFreqList = []
    while(cpu_core_number > 0):
        commandList.append('adb shell cat /sys/devices/system/cpu/cpu{}/cpufreq/scaling_cur_freq'.format(cpu_core_number - 1))
        cpu_core_number = cpu_core_number - 1
    for command in commandList:
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        out = p.stdout.readline()
        result = out.decode('utf-8').strip()
        cpuFreqList.append(result)
    print(cpuFreqList[::-1])
    return cpuFreqList[::-1]



def main():
    with open("result.csv", "w", newline='') as file:
        writer = csv.writer(file)
        cpu_core_num = 8
        i = 0
        j = 0
        row = ['时间', '系统CPU占用', '系统内存占用']
        while(j < cpu_core_num):
            row.append('cpu' + str(j))
            j = j + 1
        writer.writerow(row)
        while(i < 10 * 60):
            cpu_info = get_phone_cpu_info3()
            mem_info = get_phone_memory_info()
            cpu_freq = get_cpu_freg(cpu_core_num)
            ct = get_current_time()
            writer.writerow([ct, cpu_info, mem_info] + cpu_freq)
            time.sleep(5)
            i = i + 5




if __name__ == '__main__':
    main()