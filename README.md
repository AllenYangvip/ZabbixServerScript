# ZabbixServerScript
##
##此项目为ZabbixServer端的脚本，包含有微信报警脚本和IPMI服务器硬件状态
## 此项目为ZabbixServer端的脚本，包含有微信报警脚本和IPMI服务器硬件状态
## 目录结构：
<<<<<<< HEAD
###### .
###### ├── AlertScripts           报警脚本所在包
###### │   ├── __init__.py
###### │   └── ZabbixAlert.py     微信报警脚本
###### └── ExecScripts            监控脚本所在包
######     ├── __init__.py
######     ├── IPMIScript2.py     改良版的通过IPMI获取硬件信息的主脚本
######     ├── IPMIScript.py      
######     ├── read_item.py       读取硬件信息的辅助脚本
######     └── test.py

######  IPMI详情：
######  该版本已经是我做的第三版了，因为Zabbix通过自身的IPMI监控获取硬件，总是出现中断现象。于是，部门领导将改进任务交给了我，在我研究下。
######  略有小成。比自身监控有了明显的提升。
######  IPMI具体实施步骤：
######   1.修改zabbix-Server的配置文件，将Timeout值修改为30
######   2.将IPMIScript2.py read_item.py 文件复制到Zabbix调用外部脚本的目录下（例如：/usr/lib/zabbix/externalscripts/）
######     修改所属主组为zabbix  例如：chown zabbix:zabbix *.py  权限为777  chmod 777 *.py
######   3.在要zabbi web端监控的主机的监控项中添加一项 IPMIScript2.py["{HOST.IP}","用户名","密码","获取硬件的键","硬件的值" ]
######    （例如：IPMIScript2.py["{HOST.IP}","administrator","123456789","Power Supply 1","value" ]）
######   4.可添加多项 read_item.py[{HOST.IP},"获取硬件的键","硬件的值"]   例如：read_item.py[{HOST.IP},"01-Inlet Ambient","status"]
######    注意：我在脚本中添加了两种值一种是  value：即硬件本身所带有的值   status：硬件的状态。这两个则是IPMI监控硬件最重要的性能指标。
######    具体内容可用命令：ipmitool -I lanplus -H IP地址 -U 用户名 -P密码 sensor list  查看。

###### key值               value        单位         status

###### UID Light        | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na        
###### Sys. Health LED  | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na        
###### Power Supply 1   | 145        | Watts      | ok    | na        | na        | na        | na        | na        | na        
###### Power Supply 2   | na         | discrete   | na    | na        | na        | na        | na        | na        | na        
###### Power Supplies   | 0x0        | discrete   | 0x0880| na        | na        | na        | na        | na        | na        
###### Fan 1            | 9.800      | percent    | ok    | na        | na        | na        | na        | na        | na        
###### Fan 2            | 12.936     | percent    | ok    | na        | na        | na        | na        | na        | na 
