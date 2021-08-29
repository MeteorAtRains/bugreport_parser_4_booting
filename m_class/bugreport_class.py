import re
from datetime import datetime
from typing import Any, Dict, List, TextIO, Tuple, Union

_DEBUG_ = False

class BugreportParsedResult:
    __RE_END = re.compile(r'------ .* ------')
    __RE_DUMPSTATE = re.compile(r'== dumpstate: '
                                r'(?P<dumpstate>[0-9]+-[0-9]+-[0-9]+ [0-9:]+)')

    __RE_UPTIME = re.compile(
        r"Uptime: +up +(?P<weeks>\d+) +weeks?, +(?P<days>\d+) +days?, +"
        r"(?P<hours>\d+) +hours?, +"
        r"(?P<minutes>\d+) +minutes?")
    __RE_UPTIME_1 = re.compile(r"------ UPTIME \(uptime\) ------")
    __RE_UPTIME_2 = re.compile(r" +[0-9:]+ +(?P<uptime>up *([0-9]+ +days?,)? *[0-9:]+),"
                               r" +0 users, +load average: .*")
    __RE_UPTIME_3 = re.compile(r" +[0-9:]+ (?P<uptime>up +[0-9]+ +min), +"
                               r"0 users, +load average: .*")
    __RE_KNERNEL_VERSION = re.compile(r'Kernel: Linux version '
                                      r'(?P<kernel_version>[0-9.]+).*'
                                      r'(?P<compile>[a-zA-Z]{3} [0-9]{1,2}) '
                                      r'[0-9:]{8} [a-zA-Z]+ [0-9]+')

    __RE_LOGCAT_BEGIN = re.compile(
        r'------ SYSTEM LOG \(logcat -v threadtime -v printable( -v '
        r'uid)? -d \*:v\) ------')
    __RE_LOGCAT = re.compile(
        r'(?P<month>\d{2})-(?P<day>\d{2}) (?P<hour>\d{2}):(?P<minute>\d{2})'
        r':(?P<second>\d{2}).(?P<millisecond>\d{3})'
        r'( +(?P<uid>.+?))? +(?P<pid>.+?) +(?P<tid>.+?) +(?P<priority>.)'
        r' +(?P<tag>.*?) *: +(?P<message>.*)')
    __RE_LOGCAT_END = re.compile(
        r'------ ?[0-9.]+s was the duration of \'SYSTEM LOG\' ------')

    __RE_KERNEL_LOG_LOGCAT_BEGIN = re.compile(
        r'------ KERNEL LOG \(logcat -b kernel -v threadtime -v ' 
        r'printable -v uid -d \*:v\) ------')
    __RE_KERNEL_LOG_DMESG_BEGIN = re.compile(r'------ KERNEL LOG \(dmesg\) ------')
    __RE_KERNEL_LOG = re.compile(
        r'(?P<month>\d{2})-(?P<day>\d{2}) (?P<hour>\d{2}):(?P<minute>\d{2})'
        r':(?P<second>\d{2}).(?P<millisecond>\d{3})'
        r' +(?P<uid>.+?) +(?P<pid>.+?) +(?P<tid>.+?) +(?P<priority>.*?):'
        r' *(?P<message>.*)' )
    __RE_KERNEL_LOG_DMESG = re.compile(r'<[0-9]+>\[ *(?P<time>[0-9.]+)\] '
                                       r'+(?P<message>.*)')
    __RE_KERNEL_LOG_END = re.compile(
        r'------ ?[0-9.]+s was the duration of \'KERNEL LOG .*\' ------')

    __RE_ION_BEGIN = re.compile(r'---- +ION Memory Usage +----')
    __RE_ION_END = re.compile(r'---- +End of ION Memory Usage +----')

    __RE_DUMPSYS_MEMINFO_BEGIM = re.compile(
        r'Applications Memory Usage \(in Kilobytes\):')
    __RE_DUMPSYS_MEMINFO_END_QP = re.compile(
        r'--------- [0-9.]+s was the duration of '
        r'dumpsys meminfo, ending at: (\d{4})'
        r'-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})' )
    __RE_DUMPSTATE_MEMINFO_END_ON = re.compile(r'------ ?[0-9.]+s was the '
                                              r'duration of \'DUMPSYS MEMINFO\' '
                                              r'------')

    __RE_MEMINFO_BEGIN = re.compile(r'------ MEMORY INFO \(/proc/meminfo\) ------')
    __RE_MEMINFO = re.compile(r'(?P<name>[A-Za-z_()]+): *(?P<size>\d+) ?kB')
    __RE_MEMINFO_END = re.compile(
        r'------ ?[0-9.]+s was the duration of \'MEMORY INFO\' ------')

    # __RE_DUMPSYS_CPUINFO_BEGIN =
    __RE_DUMPSYS_CPUINFO_END_PQ = re.compile(
        r'--------- [0-9.]+s was the duration of '
        r'dumpsys cpuinfo, ending at: (\d{4})'
        r'-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})')
    __RE_DUMPSYS_CPUINFO_END_ON = re.compile(r'------ ?[0-9.]+s was the '
                                              r'duration of \'DUMPSYS CPUINFO\' '
                                              r'------')


    __RE_FREE_SPACE_BEGIN = re.compile(r'------ FILESYSTEMS & FREE SPACE \(df\)'
                                       r' ------')
    __RE_FREE_SPACE_END = re.compile(r'------ ?[0-9.]+s was the duration of'
                                     r' \'FILESYSTEMS & FREE SPACE\' ------')
    __RE_FREE_SPACE_DATA = re.compile(r'.* +(?P<total_storage>[0-9]+) +[0-9]+ '
                                      r'+[0-9]+ +(?P<data_usage>[0-9]+)% '
                                      r'+/data(\n)?')

    __RE_PACKAGE_WARNING_MESSAGES_BEGIN = re.compile(r'Package warning messages:')
    __RE_PACKAGE_WARNING_MESSAGES = re.compile(r'(?P<year>[0-9]+)/(?P<month>[0-9]+)/(?P<day>[0-9]+) '
                                               r'+(?P<noon>.*?)(?P<hour>[0-9]+):(?P<min>[0-9]+): +(?P<message>.*)')
    __RE_OTA = re.compile(r'Upgrading +from +(?P<message1>.*) +to +(?P<message2>.*)')

    __RE_SERVICE_DISPLAY_BEGIN = re.compile(r'DUMP +OF +SERVICE +display:')
    __RE_SERVICE_DISPLAY_END = re.compile(r'--------- ?[0-9.]+s was the '
                                          r'duration of dumpsys display, '
                                          r'ending at: +\d{4}-\d{2}-\d{2} '
                                          r'+\d{2}:\d{2}:\d{2}')
    __RE_DATA_STORE = re.compile(r'PersistentDataStore')
    __RE_RESOLUTION_WIDTH = re.compile(r' +StableDisplayWidth='
                                       r'(?P<resolution_width>\d+)')
    __RE_RESOLUTION_HEIGHT = re.compile(r' +StableDisplayHeight='
                                        r'(?P<resolution_height>\d+)')

    __RE_SYSTEM_PROPERTIES_BEGIN = re.compile(r'------ +SYSTEM PROPERTIES( \(getprop\))?'
                                        r' +------')
    __RE_SYSTEM_PROPERTIES = re.compile(r'\[(?P<pro_key>.*)\]: '
                                        r'+\[(?P<pro_value>.*)\]')
    __RE_SYSTEM_PROPERTIES_END = re.compile(r'------ [0-9.]+s was the duration'
                                            r' of \'SYSTEM PROPERTIES\' ------')

    __RE_ACTIVITY_PROCESS_BEGIN = re.compile(r'ACTIVITY MANAGER RUNNING '
                                             r'PROCESSES \(dumpsys activity '
                                             r'processes\)')
    __RE_PID_MAPPING = re.compile(r' +PID #[0-9]+: +ProcessRecord{[0-9a-zA-Z]+ '
                                  r'(?P<pid>[0-9]+):(?P<process>.*)?/'
                                  r'(?P<process_status>.*)?}')
    __RE_ACTIVITY_PROCESS_END = re.compile(r'------------------------+')
    __RE_EVENT_LOG_BEGIN = re.compile(r'------ +EVENT +LOG +\(logcat.*')
    __RE_EVENT_LOG = re.compile(r'(?P<month>\d{2})-(?P<day>\d{2}) '
                                r'(?P<hour>\d{2}):(?P<minute>\d{2}):'
                                r'(?P<second>\d{2}).(?P<millisecond>\d{3})'
                                r'( +(?P<uid>.+?))? +(?P<pid>.+?) '
                                r'+(?P<tid>.+?) +(?P<priority>.) '
                                r'(?P<tag>.*?) *: +(?P<message>.*)')
    __RE_EVENT_LOG_END = re.compile(r'------ [0-9.]+s was the duration of '
                                    r'\'EVENT LOG\' ------')

    __RE_MINFREE_AND_ADJ_BEGIN = re.compile(r'---- minfree & adj ----')
    __RE_MINFREE_AND_ADJ_END = re.compile(r'---- End of minfree & adj ----')
    __RE_MINFREE_AND_ADJ = re.compile(r' *(?P<key>[a-zA-Z]+): *(?P<value>.*)')

    def __logcat_begin(self, line):
        r_logcat_begin = BugreportParsedResult.__RE_LOGCAT_BEGIN.match(line)
        if r_logcat_begin:
            self.__link['SYSTEM LOG begin'] = self.__line_no
        return r_logcat_begin

    def __logcat_parse(self, line):
        r_logcat = BugreportParsedResult.__RE_LOGCAT.match(line)
        if r_logcat:
            if r_logcat.group('uid'):
                log_entry = {
                    'time': datetime(
                        year=2020, month=int(r_logcat.group('month')),
                        day=int(r_logcat.group('day')),
                        hour=int(r_logcat.group('hour')),
                        minute=int(r_logcat.group('minute')),
                        second=int(r_logcat.group('second')),
                        microsecond=1000 * int(r_logcat.group('millisecond'))
                    ),
                    'uid': r_logcat.group('uid'),
                    'pid': r_logcat.group('pid'),
                    'tid': r_logcat.group('tid'),
                    'priority': r_logcat.group('priority'),
                    'tag': r_logcat.group('tag'),
                    'message': r_logcat.group('message')
                }
                self.__logcat.append((self.__line_no, log_entry, line))
            else:
                log_entry = {
                    'time': datetime(
                        year=2020, month=int(r_logcat.group('month')),
                        day=int(r_logcat.group('day')),
                        hour=int(r_logcat.group('hour')),
                        minute=int(r_logcat.group('minute')),
                        second=int(r_logcat.group('second')),
                        microsecond=1000 * int(r_logcat.group('millisecond'))
                    ),
                    'pid': r_logcat.group('pid'),
                    'tid': r_logcat.group('tid'),
                    'priority': r_logcat.group('priority'),
                    'tag': r_logcat.group('tag'),
                    'message': r_logcat.group('message')
                }
                self.__logcat.append((self.__line_no, log_entry, line))

    def __logcat_end(self, line):
        r_logcat_end = BugreportParsedResult.__RE_LOGCAT_END.match(line)
        r_end = BugreportParsedResult.__RE_END.match(line)
        if r_logcat_end or r_end:
            self.__link['SYSTEM LOG end'] = self.__line_no
        return r_logcat_end

    def __kernel_log_begin(self, line):
        r_kernel_log_begin_logcat = BugreportParsedResult.__RE_KERNEL_LOG_LOGCAT_BEGIN.match(line)
        r_kernel_log_begin_dmesg = BugreportParsedResult.__RE_KERNEL_LOG_DMESG_BEGIN.match(line)
        if r_kernel_log_begin_logcat or r_kernel_log_begin_dmesg:
            self.__link['KERNEL LOG begin'] = self.__line_no
            return True
        return False

    def __kernel_log_parse(self, line):
        r_kernel = BugreportParsedResult.__RE_KERNEL_LOG.match(line)
        r_kernel_dmesg = BugreportParsedResult.__RE_KERNEL_LOG_DMESG.match(line)
        if r_kernel:
            log_entry = {
                'time': datetime(
                    year=2020, month=int(r_kernel.group('month')),
                    day=int(r_kernel.group('day')),
                    hour=int(r_kernel.group('hour')),
                    minute=int(r_kernel.group('minute')),
                    second=int(r_kernel.group('second')),
                    microsecond=
                    1000 * int(r_kernel.group('millisecond'))
                ),
                'uid': r_kernel.group('uid'),
                'pid': r_kernel.group('pid'),
                'tid': r_kernel.group('tid'),
                'priority': r_kernel.group('priority'),
                'message':
                    r_kernel.group('message')
            }
            self.__kernel_log.append((self.__line_no, log_entry, line, 'logcat'))
        elif r_kernel_dmesg:
            log_entry = {
                'time': r_kernel_dmesg.group('time'),
                'message': r_kernel_dmesg.group('message')
            }
            self.__kernel_log.append((self.__line_no, log_entry, line, 'dmesg'))

    def __kernel_log_end(self, line):
        r_end = BugreportParsedResult.__RE_END.match(line)
        r_kernel_log_end = BugreportParsedResult.__RE_KERNEL_LOG_END.match(line)
        if r_kernel_log_end or r_end:
            self.__link['KERNEL LOG end'] = self.__line_no
            return True
        return False

    def __dumpsys_meminfo_begin(self, line):
        r_dumpsys_meminfo_begin = BugreportParsedResult.__RE_DUMPSYS_MEMINFO_BEGIM.match(line)
        if r_dumpsys_meminfo_begin:
            self.__link['Applications Memory Usage begin'] = self.__line_no
        return r_dumpsys_meminfo_begin

    def __dumpsys_meminfo_parse(self, line):
        self.__dumpsys_meminfo.append((self.__line_no, line))
        if line.startswith('Total RAM: '):
            if 'total_ram' not in self.__basic_info.keys():
                total_ram = re.match(r'Total RAM: (?P<total_ram>[0-9,]+K .*)',
                                    line)['total_ram']
                ram = int(total_ram.split(',')[0]) + 1
                self.__basic_info['total_ram'] = (self.__line_no, ram)
            self.link[line.replace('\n', '')] = self.__line_no


    def __dumpsys_meminfo_end(self, line):
        r_end = BugreportParsedResult.__RE_END.match(line)
        r_dumpsys_meminfo_end_QP = BugreportParsedResult.__RE_DUMPSYS_MEMINFO_END_QP.match(line)
        r_dumpsys_meminfo_end_NO = BugreportParsedResult.__RE_DUMPSTATE_MEMINFO_END_ON.match(line)
        if r_dumpsys_meminfo_end_QP or r_end or r_dumpsys_meminfo_end_NO:
            self.__link['Applications Memory Usage end'] = self.__line_no
            return True
        return False

    def __dumpsys_cpuinfo_begin(self, line: str):
        if line.startswith('Load:'):
            self.__link['CPU usage'] = self.__line_no+1
        return line.startswith('Load:')

    def __dumpsys_cpuinfo_parse(self, line):
        self.__dumpsys_cpuinfo.append((self.__line_no, line))
        pass

    def __dumpsys_cpuinfo_end(self, line):
        r_dumpsys_cpu_info_end_PQ = BugreportParsedResult.__RE_DUMPSYS_CPUINFO_END_PQ.match(line)
        r_dumpsys_cpu_info_end_ON = BugreportParsedResult.__RE_DUMPSYS_CPUINFO_END_ON.match(line)
        if r_dumpsys_cpu_info_end_PQ or r_dumpsys_cpu_info_end_ON:
            return True
        return False

    def __meminfo_begin(self, line):
        r_meminfo_begin = BugreportParsedResult.__RE_MEMINFO_BEGIN.match(line)
        if r_meminfo_begin:
            self.__link['MEMORY INFO'] = self.__line_no
        return r_meminfo_begin

    def __meminfo_parse(self, line):
        r_meminfo = BugreportParsedResult.__RE_MEMINFO.match(line)
        if r_meminfo:
            self.__meminfo[r_meminfo.group('name')] = \
                (self.__line_no, int(r_meminfo.group('size')), line)
            if 'total_ram' not in self.__basic_info.keys():
                if r_meminfo.group('name') == 'MemTotal':
                    ram = int(int(r_meminfo.group('size'))/(1024*1024)) + 1
                    self.__basic_info['total_ram'] = (self.__line_no, ram)
        pass

    def __meminfo_end(self, line: str):
        r_end = BugreportParsedResult.__RE_END.match(line)
        r_meminfo_end = BugreportParsedResult.__RE_MEMINFO_END.match(line)
        if r_meminfo_end or r_end:
            return True
        return False

    def __free_space_begin(self, line):
        r_free_space_begin = BugreportParsedResult.__RE_FREE_SPACE_BEGIN.match(line)
        return r_free_space_begin

    def __free_space_parse(self, line):
        self.__free_space.append((self.__line_no, line))
        r_data = self.__RE_FREE_SPACE_DATA.match(line)
        if r_data:
            data_usage = int(r_data.group('data_usage'))
            for i in range(0, 10):
                if i*10 <= data_usage < (i+1)*10:
                    self.__basic_info['data_partition_usage'] = i*10
            total_storage = int(r_data.group('total_storage'))
            gb = 1024*1024
            if 0 <= total_storage < 4*gb:
                self.__basic_info['total_storage'] = (self.__line_no, '4G')
            elif 4*gb <= total_storage < 8*gb:
                self.__basic_info['total_storage'] = (self.__line_no, '8G')
            elif 8*gb <= total_storage < 16*gb:
                self.__basic_info['total_storage'] = (self.__line_no, '16G')
            elif 16*gb <= total_storage < 32*gb:
                self.__basic_info['total_storage'] = (self.__line_no, '32G')
            elif 32*gb <= total_storage < 64*gb:
                self.__basic_info['total_storage'] = (self.__line_no, '64G')
            elif 64*gb <= total_storage < 128*gb:
                self.__basic_info['total_storage'] = (self.__line_no, '128G')
            elif 128*gb <= total_storage < 256*gb:
                self.__basic_info['total_storage'] = (self.__line_no, '256G')
            elif 256*gb <= total_storage < 512*gb:
                self.__basic_info['total_storage'] = (self.__line_no, '512G')
            else:
                self.__basic_info['total_storage'] = (self.__line_no, '-1')

    def __free_space_end(self, line):
        r_end = BugreportParsedResult.__RE_END.match(line)
        r_free_space_end = BugreportParsedResult.__RE_FREE_SPACE_END.match(line)
        if r_end or r_free_space_end:
            return True
        return False

    def __package_warning_message_begin(self, line):
        r_begin = BugreportParsedResult.__RE_PACKAGE_WARNING_MESSAGES_BEGIN.match(line)
        return r_begin

    def __package_warning_message_end(self, line):
        '''
        r_end = self.__RE_PACKAGE_WARNING_MESSAGES.match(line)
        return not r_end
        '''
        r_end = BugreportParsedResult.__RE_END.match(line)
        return r_end

    def __package_warning_message(self, line):
        r = self.__RE_PACKAGE_WARNING_MESSAGES.match(line)
        try:
            if r:
                r_ota = self.__RE_OTA.match(r['message'])
                if r_ota:
                    if r['noon'] != '':
                        hour = r['hour']
                        if r['noon'] == '上午' and int(hour) == 12:
                            hour = '00'
                        elif r['noon'] == '下午' and int(hour) == 12:
                            pass
                        elif r['noon'] == '下午':
                            hour = int(hour) + 12

                        OTA = '{year}-{month}-{day} {hour}:{min}:00'\
                             .format(year=r['year'], month=r['month'], day=r['day'],
                                     hour=hour, min=r['min'])
                    elif r['noon'] == '':
                        if len(r['year']) == 2 and len(r['month']) == 2 \
                                and len(r['day']) == 4:
                            OTA = '{year}-{month}-{day} {hour}:{min}:00'\
                                .format(year=r['day'], month=r['month'],
                                        day=r['year'], hour=r['hour'], min=r['min'])
                    after_OTA_run = datetime.strptime(OTA, '%Y-%m-%d %H:%M:%S')
                    if self.__basic_info['OTA'][1] == -1 \
                            or self.__basic_info['OTA'][1] < after_OTA_run:
                        self.__basic_info['OTA'] = (self.__line_no, after_OTA_run,
                                                    r_ota['message2'])
        except:
            self.__basic_info['OTA'] = ('null', 'null', 'null')

    def __ion_memory_begin(self, line):
        r_begin = BugreportParsedResult.__RE_ION_BEGIN.match(line)
        return r_begin

    def __ion_memory_end(self, line):
        r_end = BugreportParsedResult.__RE_END.match(line)
        r_ion_end = BugreportParsedResult.__RE_ION_END.match(line)
        if r_end or r_ion_end:
            return True
        return False

    def __ion_parse(self, line):
        self.__ion_memory.append((self.__line_no, line))

    def __service_display_begin(self, line):
        r_begin = BugreportParsedResult.__RE_SERVICE_DISPLAY_BEGIN.match(line)
        return r_begin

    def __service_display_end(self, line):
        r_end = BugreportParsedResult.__RE_END.match(line)
        r_service_display_end = BugreportParsedResult.\
            __RE_SERVICE_DISPLAY_END.match(line)
        if r_end or r_service_display_end:
            return True
        else:
            return False

    def __service_display_parse(self, line):
        r_width = BugreportParsedResult.__RE_RESOLUTION_WIDTH.match(line)
        r_height = BugreportParsedResult.__RE_RESOLUTION_HEIGHT.match(line)
        if 'resolution' not in self.__basic_info.keys():
            self.__basic_info['resolution'] = {'width': '-1', 'height': '-1'}
        if r_width:
            self.__basic_info['resolution']['width'] = \
                r_width.group('resolution_width')
        elif r_height:
            self.__basic_info['resolution']['height'] = \
                r_height.group('resolution_height')

    def __system_properties_begin(self, line):
        r_begin = BugreportParsedResult.__RE_SYSTEM_PROPERTIES_BEGIN.match(line)
        return r_begin

    def __system_properties_end(self, line):
        r_end = BugreportParsedResult.__RE_END.match(line)
        r_properties_end = \
            BugreportParsedResult.__RE_SYSTEM_PROPERTIES_END.match(line)
        if r_end or r_properties_end:
            return True
        else:
            return False

    def __system_properties_parse(self, line):
        r = BugreportParsedResult.__RE_SYSTEM_PROPERTIES.match(line)
        if r:
            self.__system_properties[r.group('pro_key')] = (self.__line_no,
                                                      r.group('pro_value'), line)
            key = r.group('pro_key')
            value = r.group('pro_value')
            if key == 'ro.board.platform':
                self.__basic_info['platform'] = (self.__line_no, value)
            elif key == 'ro.debuggable':
                self.__basic_info['isROOT'] = (self.__line_no, value == '1')
            elif (key == 'persist.sys.mem_cgated' and value == '0') or \
                    (key == 'persist.sys.mem_fgated' and value == '0'):
                self.__basic_info['defrag'] = True
            elif key == 'ro.bootimage.build.fingerprint':
                r_build = re.match(r'([xX]iaomi|Redmi|Meitu|.*)/(?P<name>[a-zA-Z_]+)'
                                      r'/[a-zA-Z_]+:(?P<android>[0-9.]+)/'
                                      r'[a-zA-Z0-9.]+/'
                                      r'(?P<miui_version>[a-zA-Z0-9.]+):'
                                      r'[a-zA-Z]+/.*', value)
                if r_build:
                    self.__basic_info['name'] = \
                        (self.__line_no, r_build.group('name'))
                    self.__basic_info['android'] = \
                        (self.__line_no, r_build.group('android'))
                    self.__basic_info['miui_version'] = \
                        (self.__line_no, r_build.group('miui_version'))
            elif key == 'ro.product.model':
                self.__basic_info['model'] = (self.__line_no, value)
            elif key in ['ro.ril.miui.imei0', 'ro.ril.miui.imei1',
                         'ro.ril.oem.imei', 'ro.ril.oem.imei1',
                         'ro.ril.oem.imei2']:
                if 'imei' not in self.__basic_info.keys():
                    self.__basic_info['imei'] = (self.__line_no, value)
                else:
                    imei_origin = self.__basic_info['imei'][1]
                    if value > imei_origin:
                        self.__basic_info['imei'] = (self.__line_no, value)

    def __dumpsys_activity_process_begin(self, line):
        r_begin = BugreportParsedResult.__RE_ACTIVITY_PROCESS_BEGIN.match(line)
        return r_begin

    def __dumpsys_activity_process_end(self, line):
        r_end = BugreportParsedResult.__RE_SYSTEM_PROPERTIES_END.match(line)
        return r_end

    def __dumpsys_activity_process_parse(self, line):
        r = BugreportParsedResult.__RE_PID_MAPPING.match(line)
        if r:
            self.__pid_mappings.append((self.__line_no,
                                        {'pid': r.group('pid'),
                                         'process': r.group('process'),
                                         'process_status': r.group('process_status'),
                                        },
                                        line
                                        ))

    def __event_log_begin(self, line):
        r_begin = BugreportParsedResult.__RE_EVENT_LOG_BEGIN.match(line)
        if r_begin:
            self.__link['EVENT LOG begin'] = self.__line_no
        return r_begin

    def __event_log_end(self, line):
        r_event_end = BugreportParsedResult.__RE_EVENT_LOG_END.match(line)
        r_end = BugreportParsedResult.__RE_END.match(line)
        if r_event_end or r_end:
            self.__link['EVENT LOG end'] = self.__line_no
            return True
        return False

    def __event_log_parse(self, line):
        r_event = BugreportParsedResult.__RE_EVENT_LOG.match(line)
        if r_event:
            if r_event.group('uid'):
                log_entry = {
                    'time': datetime(
                        year=2020, month=int(r_event.group('month')),
                        day=int(r_event.group('day')),
                        hour=int(r_event.group('hour')),
                        minute=int(r_event.group('minute')),
                        second=int(r_event.group('second')),
                        microsecond=1000 * int(r_event.group('millisecond'))
                    ),
                    'uid': r_event.group('uid'),
                    'pid': r_event.group('pid'),
                    'tid': r_event.group('tid'),
                    'priority': r_event.group('priority'),
                    'tag': r_event.group('tag'),
                    'message': r_event.group('message')
                }
                self.__event_log.append((self.__line_no, log_entry, line))
            else:
                log_entry = {
                    'time': datetime(
                        year=2020, month=int(r_event['month']),
                        day=int(r_event['day']),
                        hour=int(r_event['hour']),
                        minute=int(r_event['minute']),
                        second=int(r_event['second']),
                        microsecond=1000 * int(r_event['millisecond'])
                    ),
                    'pid': r_event.group('pid'),
                    'tid': r_event.group('tid'),
                    'priority': r_event.group('priority'),
                    'tag': r_event.group('tag'),
                    'message': r_event.group('message')
                }
                self.__event_log.append((self.__line_no, log_entry, line))
            if 'wm_boot_animation_done' not in self.__basic_info.keys():
                if r_event.group('tag') == 'wm_boot_animation_done':
                    self.__basic_info['wm_boot_animation_done'] = \
                        (self.__line_no, str(int(r_event.group('message'))/1000)+'s')

    def __minfree_and_adj_begin(self, line):
        r_begin = BugreportParsedResult.__RE_MINFREE_AND_ADJ_BEGIN.match(line)
        if r_begin:
            self.__link['MINFREE AND ADJ BEGIN'] = self.__line_no
        return r_begin

    def __minfree_and_adj_end(self, line):
        r_end = BugreportParsedResult.__RE_END.match(line)
        if '---- End of minfree & adj ----' in line or r_end:
            self.__link['MINFREE AND ADJ END'] = self.__line_no
            return True
        return False

    def __minfree_and_adj_parse(self, line):
        r = BugreportParsedResult.__RE_MINFREE_AND_ADJ.match(line)
        if r:
            self.__minfreeAndAdj[r.group('key')] = (self.__line_no,
                                              r.group('value'), line)

    def __init__(self, fd: TextIO):
        self.__uptime = tuple()
        self.__basic_info = dict()
        self.__logcat = list()
        self.__kernel_log = list()
        self.__event_log = list()
        self.__dumpsys_meminfo = list()
        self.__meminfo = dict()
        self.__system_properties = dict()
        self.__dumpsys_cpuinfo = list()
        self.__free_space = list()
        self.__ion_memory = list()
        self.__pid_mappings = list()
        self.__minfreeAndAdj = dict()
        self.__link = dict()
        self.__line_no = 0
        self.__parse(fd)

    def __parse(self, fd):
        # likes = [
        #     [self.__kernel_log_begin, self.__kernel_log_parse,
        #      self.__kernel_log_end, 0, "KERNEL_LOG"],
        # ]

        likes = [[self.__logcat_begin, self.__logcat_parse,
                  self.__logcat_end, 0, "LOGCAT"],
                 [self.__kernel_log_begin, self.__kernel_log_parse,
                  self.__kernel_log_end, 0, "KERNEL_LOG"],
                 [self.__dumpsys_meminfo_begin, self.__dumpsys_meminfo_parse,
                  self.__dumpsys_meminfo_end, 0, "DUMPSYS_MEMINFO"],
                 [self.__meminfo_begin, self.__meminfo_parse,
                  self.__meminfo_end, 0, "MEMINFO"],
                 [self.__dumpsys_cpuinfo_begin, self.__dumpsys_cpuinfo_parse,
                  self.__dumpsys_cpuinfo_end, 0, "DUMPSYS_CPUINFO"],
                 [self.__free_space_begin, self.__free_space_parse,
                  self.__free_space_end, 0, "FREE_SPACE"],
                 [self.__package_warning_message_begin,
                  self.__package_warning_message,
                  self.__package_warning_message_end, 0,
                  "PACKAGE_WARNING_MESSAGE"],
                 [self.__ion_memory_begin, self.__ion_parse,
                  self.__ion_memory_end, 0, "ION_MEMORY"],
                 [self.__service_display_begin, self.__service_display_parse,
                  self.__service_display_end, 0, "SERVICE_DISPLAY"],
                 [self.__system_properties_begin,
                  self.__system_properties_parse,
                  self.__system_properties_end, 0, 'SYSTEM_PROPERTIES'],
                 [self.__dumpsys_activity_process_begin,
                  self.__dumpsys_activity_process_parse,
                  self.__dumpsys_activity_process_end, 0,
                  'DUMPSYS_ACTIVITY_PROCESS'],
                 [self.__event_log_begin, self.__event_log_parse,
                  self.__event_log_end, 0, 'EVENT_LOG'],
                 [self.__minfree_and_adj_begin, self.__minfree_and_adj_parse,
                  self.__minfree_and_adj_end, 0, 'MINFREE & ADJ']
                 ]

        flag_uptime = 0
        for line in fd:
            self.__line_no += 1
            for kind in likes:
                if kind[3] == 0:
                    if kind[0](line):
                        kind[3] = 1
                        if _DEBUG_:
                            print("调试信息："+kind[4]+" begins @"+str(self.__line_no))
                elif kind[3] == 1:
                    if kind[2](line):
                        kind[3] = 2
                        if _DEBUG_:
                            print("调试信息："+kind[4]+" ends @"+str(self.__line_no))
                    else:
                        kind[1](line)
            #
            if self.__uptime is None:
                r_uptime = BugreportParsedResult.__RE_UPTIME.match(line)
                r_uptime_1 = BugreportParsedResult.__RE_UPTIME_1.match(line)
                line_str = line.split(':')[-1].strip()
                if r_uptime:
                    weeks, days, hours, minutes = \
                        map(int, (r_uptime['weeks'], r_uptime['days'],
                                  r_uptime['hours'], r_uptime['minutes']))
                    time = ((weeks * 7 + days) * 24 + hours) * 60 + minutes
                    self.__uptime = (self.__line_no, line_str, time)
                elif r_uptime_1:
                    flag_uptime = 1
                    continue
                elif flag_uptime == 1:
                    r_uptime_2 = BugreportParsedResult.__RE_UPTIME_2.match(line)
                    if r_uptime_2:
                        line_str = r_uptime_2['uptime']
                        if 'day' in line_str:
                            days = int(line_str.split(' ')[1])
                            hours = int(line_str.split(' ')[-1].split(':')[0])
                            minutes = int(line_str.split(' ')[-1].split(':')[1])
                            time = (days * 24 + hours) * 60 + minutes
                        else:
                            hours = int(line_str.split(' ')[-1].split(':')[0])
                            minutes = int(line_str.split(' ')[-1].split(':')[1])
                            time = hours * 60 + minutes
                        self.__uptime = (self.__line_no, line_str, time)
                    else:
                        r_uptime_3 = BugreportParsedResult.__RE_UPTIME_3.match(line)
                        if r_uptime_3:
                            line_str = r_uptime_3['uptime']
                            time = int(line_str.split(' ')[1])
                            self.__uptime = (self.__line_no, line_str, time)
                    flag_uptime = 0
                    continue

            if 'dumpstate' not in self.__basic_info.keys():
                r_dumpstate = BugreportParsedResult.__RE_DUMPSTATE.match(line)
                if r_dumpstate is not None:
                    self.__basic_info['dumpstate'] = \
                        (self.__line_no, r_dumpstate.group('dumpstate'))
                    continue
            if "kernel_version" not in self.__basic_info.keys():
                r_kernel = BugreportParsedResult.__RE_KNERNEL_VERSION.match(line)
                if r_kernel is not None:
                    self.__basic_info['kernel_version'] = \
                        (self.__line_no, r_kernel.group('kernel_version'))
                    self.__basic_info['compile'] = \
                        (self.__line_no, r_kernel.group('compile'))
                    continue





    @property
    def uptime(self) -> Tuple[int, str, int]:
        return self.__uptime

    @property
    def logcat(self) -> List[Tuple[int, Dict[str, Any], str]]:
        return self.__logcat

    @property
    def kernel_log(self) -> List[Tuple[int, Dict, str]]:
        return self.__kernel_log

    @property
    def dumpsys_meminfo(self) -> List[Tuple[int, str]]:
        return self.__dumpsys_meminfo

    @property
    def dumpsys_cpuinfo(self) -> List[Tuple[int, str]]:
        return self.__dumpsys_cpuinfo

    @property
    def meminfo(self) -> Dict[str, tuple]:
        return self.__meminfo

    @property
    def basic_info(self) -> Dict:
        return self.__basic_info

    @property
    def link(self) -> Dict:
        return self.__link

    @property
    def free_space(self) -> List[Tuple[int, str]]:
        return self.__free_space

    @property
    def ion_memory(self) -> List[Tuple[int, str]]:
        return self.__ion_memory

    @property
    def pid_mappings(self) -> List[Tuple[int, Dict, str]]:
        return self.__pid_mappings

    @property
    def event_log(self) -> List[Tuple[int, Dict, str]]:
        return self.__event_log

    @property
    def system_properties(self) -> Dict[str, tuple]:
        return self.__system_properties

    @property
    def minfreeAndAdj(self) -> Dict[str, tuple]:
        return self.__minfreeAndAdj
